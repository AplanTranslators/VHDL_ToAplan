from antlr4.tree.Trees import Trees

#Data structure
class TreeStorage():
    """Tree data structure with parents and children
    """
    #keep track of instantiations
    Trees = []
    
    #internals
    ##tell __init__ a child is made, dont add to list above
    _child = False
    
    #add new root instance to list Trees above
    #initiate some variables
    def __init__(self,*args):
        name = args[0]
        if not TreeStorage._child:
            TreeStorage.Trees.append(self)
            self.type = "file"
            self.name = args[0]
        else:
            self.type = args[0]
        #parental links    
        self.children = []
        self.parent = None
        #empty dictionary
        self.data = {}
        #empty string
        self.text = ""
        #counter used for a.o. printing of tree
        self._purge = False
        self._depth = 0
    
    def delete(self):
        if self._depth == 0:
            Trees.remove(self)
        else:
            self.parent.children.remove(self)
        del self
    
    #add a child/branch to a node or tree
    #define parental relationship
    def makeChild(self, type):
        TreeStorage._child = True
        child = TreeStorage(type)
        TreeStorage._child = False
        child.parent = self
        child._depth = self._depth + 1
        self.children.append(child)
        return child
    
    #fill in text attribute of member
    def addText(self, text):
        self.text = text
    
    #add data to dictionary "data"
    def addToDataList(self, item, property):
        if item in self.data.keys():
            self.data[item].append(property)
        else:
            self.data[item] = [property]
    
    #return name of object
    def getName(self):
        return self.name
    
    #get parent of object
    def getParent(self):
        return self.parent
     
    #get children of object
    def getChildren(self):
        return self.children
        
    def getFirstChildofType(self,type):
        return [x for x in self.children if x.type == type][0]
    
    #get siblings of object, including object, also for roots
    def getSiblings(self):
        if self._depth == 0:
            return [tree for tree in TreeStorage.getTrees() if tree is not self]
        else:
            return [sibling for sibling in self.parent.children if self is not sibling]
 
    def getFirstSiblingofType(self,type):
        return [x for x in self.getSiblings() if x.type == type][0]
        
    #check if object has children
    def hasChildren(self):
        return not not self.children
        
    def hasChildNamed(self, name):
        for child in self.children:
            if child.name == name:
                return True
        return False
        
    #quick and dirty print of a tree originating from any object
    def printSubTree(self):
        text = "|   "*self._depth
        text = text + self.text
        if not self.type == "":
            text = text + " ("+self.type+")"
        print(text)
        if not self.data == {}:
            for entry in self.data.keys():
                print("|   "*self._depth + "  -> " + entry + ":" + str(self.data[entry]))
        
        if self.hasChildren():
            for child in self.children:
                child.printSubTree()     
                
    def printTree():
        for tree in TreeStorage.Trees:
            print("Root: {}".format(tree.name))
            tree.printSubTree()
    
    def getTree(name):
        return roots(name)
        
    def getTrees():
        return TreeStorage.Trees
        
    #return first ancestor of certain type, if any.
    def getAncestor(self,type):
        if self.parent is None:
            return False
        elif self.parent.type == type:
            return self.parent
        else:
            return self.parent.getAncestor(type)
                
    def hasAncestor(self,type):
        result = self.getAncestor(type)
        if result is False:
            return False
        else:
            return True
            
    def setPurge(self):
        self._purge = True

    #get all children, grandchildren etc of node
    _level = 0              
    _list = []
    def getAllChildren(self):
        TreeStorage._level = TreeStorage._level + 1
        for child in self.children:
            TreeStorage._list.append(child)
            child.getAllChildren()
        TreeStorage._level = TreeStorage._level - 1
        if TreeStorage._level == 0:
            childrenlist = TreeStorage._list
            TreeStorage._list = []
            return childrenlist
    
    #get all children, grandchildren of node with particular type
    def getAllChildrenOfType(self,type):
        return [x for x in self.getAllChildren() if x.type == type]
            
    #first step, merge Identifiers into Selected_Name
    def mergeSelectedName(self):
        for x in self.getAllChildrenOfType("Selected_name"):
            name = ""
            for y in x.getAllChildrenOfType("Identifier"):
                if not name == "":
                    name = name + "."
                name = name + y.text
                y.setPurge()
            x.text = name
        self.purge()
    
    def extractDesignUnit(self):
        for x in [x for x in self.getAllChildrenOfType("Design_unit")]:
            x.extractlib()
            x.extractuse()
            x.extractentity()
            x.extractarchitecture()
            x.purge()
        self.clean()
        
    #extract lib
    def extractlib(self):
        for x in [x for x in self.getAllChildrenOfType("Identifier") if x.hasAncestor("Library_clause")]:
            self.data.setdefault("libs",[]).append(x.text)
            x.setPurge()
        self.purge()
    
    #extract use
    #run mergeSelectedName first
    def extractuse(self):
        for x in [x for x in self.getAllChildrenOfType("Selected_name") if x.hasAncestor("Use_clause")]:
            self.data.setdefault("use",[]).append(x.text)
            x.setPurge()    
        self.purge()

    def extractentity(self):
         for x in [x for x in self.getAllChildrenOfType("Entity_declaration")]:
            x.data.setdefault("entity",[]).append(x.getFirstChildofType("Identifier").text)
            #kill end architecture XXXXX
            for y in [y for y in x.children if y.type == "Identifier"]:
                y.setPurge()
            x.purge()
            x.extractgenerics()
            x.extractentityport()
            
    #extract generics
    #run mergeSelectedName first
    def extractgenerics(self):
        for x in [x for x in self.getAllChildrenOfType("Identifier") if x.hasAncestor("Generic_clause")]:
            if x.parent.type == "Identifier_list":
                generic = x
                type = x.parent.getFirstSiblingofType("Subtype_indication").getFirstChildofType("Selected_name")
                self.data.setdefault("generic",[]).append({generic.text:type.text})
                x.setPurge()
                type.setPurge()
            elif x.parent.type == "Enumeration_literal":
                self.data.setdefault("extconstants",[]).append({x.text:"generic_constant"})
                x.setPurge()
        self.purge()
        

    #run mergeSelectedName first
    def extractentityport(self):
        for x in [x for x in self.getAllChildrenOfType("Port_clause")]:
            x.extractsignals()
            self.data.setdefault("portlist",[]).extend(x.data["signallist"])
            x.setPurge()
        self.purge()
     
    def extractarchitecture(self):
        for x in [x for x in self.getAllChildrenOfType("Architecture_body")]:
            names = [y for y in x.children if y.type == "Identifier"]
            x.data.setdefault("architecture",[]).append(names[0].text)
            x.data.setdefault("entity",[]).append(names[1].text)
            for y in names:
                y.setPurge()
            x.extractarchdeclarations()
        self.purge()
    
    def extractarchdeclarations(self):
        for x in [x for x in self.getAllChildrenOfType("Architecture_declarative_part")]:
            for y in [y for y in self.getAllChildrenOfType("Signal_declaration")]:
                y.extractsignals()
                y.setPurge()
                x.data.setdefault("signallist",[]).extend(y.data["signallist"])
                y.setPurge()
            x.purge()
            
    def extractsignals(self):
        for x in [x for x in self.getAllChildrenOfType("Identifier")]:
            if x.parent.type == "Identifier_list":
                signal = x
                type = x.parent.getFirstSiblingofType("Subtype_indication").getFirstChildofType("Selected_name")
                self.data.setdefault("signallist",[]).append({signal.text:type.text})
                x.setPurge()
                type.setPurge()
        self.purge()       
        
    #remove branches marked to purge
    def purge(self):
        #first kill the children
        for x in self.getAllChildren():
            if x._purge:
                x.delete()
        
    def clean(self):
        if self.text == "" and self.data == {} and self.children == []:
            self.delete()
            return True        
        repeat = False
        for x in self.children:
            res = x.clean()
            repeat = repeat or res      
        if repeat:
            self.clean()
        return repeat