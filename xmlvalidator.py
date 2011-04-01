import libxml2, os, re
from libxml2 import parserError, xpathError

class ValidationException(Exception):
    def __init__(self, message='Validation problem'):
        self.msg = message
        
def record_is_valid(filepath, record_type='dataset', rule_set=None):
    # Insure request is valid: record_type must be correct
    valid_types = ['dataset', 'service']
    if record_type not in valid_types:
        raise ValidationException('Requested metadata type is not valid. Valid types: ' + str(valid_types))
    
    # Insure request is valid: filepath must point to a file 
    if not os.path.exists(filepath): 
        raise ValidationException('Requested filepath to validate is not valid: ' + str(filepath))
    
    # Insure file is valid: Must be parse-able by libxml2
    try:
        doc = libxml2.parseFile(filepath)
    except parserError as (ex):
        raise ValidationException(ex.msg)
    
    # Check each Rule
    result = True
    for rule in rule_set:
        if rule.validate(doc) == False: result = False
    
    # Validation has occurred. Return the result
    doc.freeDoc()
    return result

def register_namespaces(doc):
    context = doc.xpathNewContext()
    context.xpathRegisterNs('gmd', 'http://www.isotc211.org/2005/gmd')
    context.xpathRegisterNs('gco', 'http://www.isotc211.org/2005/gco')
    context.xpathRegisterNs('gml', 'http://www.opengis.net/gml')
    context.xpathRegisterNs('xlink', 'http://www.w3.org/1999/xlink')
    context.xpathRegisterNs('xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    return context
    
class Rule():
    name = str()
    description = str()
    
    def __init__(self, name, description):
        self.name = name
        self.description = description
        
    def validate(self, doc):
        raise NotImplementedError('Needs to be implemented in derived classes')
    
class ExistsRule(Rule):
    def __init__(self, name, description, xpath):
        Rule.__init__(self, name, description)
        self.xpath = xpath
        
    def validate(self, doc):
        context = register_namespaces(doc)
        try:
            result = context.xpathEval(self.xpath)
        except xpathError:
            context.xpathFreeContext()
            return False
        
        if len(result) > 0:
            result = True
        else:
            result = False
            
        # Finished. Cleanup the context and return True
        context.xpathFreeContext()
        return result
    
class ValueInListRule(Rule):
    def __init__(self, name, description, xpath, values):
        Rule.__init__(self, name, description)
        self.xpath = xpath
        self.values = values
        
    def validate(self, doc):
        # Check that the XPath exists using an ExistsRule
        exists_rule = ExistsRule(self.name, self.description, self.xpath)
        if exists_rule.validate(doc) == False: return False
        
        # Get the XPath nodes. ExistsRule already found that the XPath is valid, so I don't need to catch xpathEval failures here.
        context = register_namespaces(doc)
        nodes = context.xpathEval(self.xpath)
        
        # Loop through them and check the values
        result = True
        for node in nodes:
            if node.content not in self.values: result = False
        
        # Finished
        context.xpathFreeContext()
        return result
    
class AnyOfRule(Rule):
    def __init__(self, name, description, xpaths):
        Rule.__init__(self, name, description)
        self.xpaths = xpaths
    
    def validate(self, doc):
        # For each XPath in xpaths, check that at least one exists using ExistsRules
        count = 0
        for xpath in self.xpaths:
            exists_rule = ExistsRule(self.name, self.description, xpath)
            if exists_rule.validate(doc) == True: count = count + 1
            
        if count > 0: 
            return True 
        else: 
            return False
        
class OneOfRule(Rule):
    def __init__(self, name, description, xpaths):
        Rule.__init__(self, name, description)
        self.xpaths = xpaths
        
    def validate(self, doc):
        # For each XPath in xpaths, check that only one exists
        count = 0
        for xpath in self.xpaths:
            exists_rule = ExistsRule(self.name, self.description, xpath)
            if exists_rule.validate(doc) == True: count = count + 1
            
        if count == 1: 
            return True 
        else: 
            return False
        
class ContentMatchesExpressionRule(Rule):
    def __init__(self, name, description, xpath, expression):
        Rule.__init__(self, name, description)
        self.xpath = xpath
        self.expression = expression
        
    def validate(self, doc):
        # Check that the XPath exists using an ExistsRule
        exists_rule = ExistsRule(self.name, self.description, self.xpath)
        if exists_rule.validate(doc) == False: return False
        
        # Get the XPath nodes. ExistsRule already found that the XPath is valid, so I don't need to catch xpathEval failures here.
        context = register_namespaces(doc)
        nodes = context.xpathEval(self.xpath)
        
        result = True
        for node in nodes:
            try:
                match = re.match(self.expression, node.content)
                # If there was no match, match will be None
                if match == None: result = False
                # If the regular expression had capture groups in it, there will be more than one. This indicates a poorly formed expression for this purpose.
                if len(match.groups()) > 1: result = False
                # If these lengths are different, then the RegEx only matched PART of the node's content.
                if len(match.group(0)) != len(node.content): result = False
            except:
                # Likely caused by an invalid expression
                return False
            
        # Finished
        context.xpathFreeContext()
        return result
    
class ConditionalRule(Rule):
    def __init__(self, name, description, rule_set):
        Rule.__init__(self, name, description)
        self.rule_set = rule_set
        
    def validate(self, doc):
        # Check that we've been given only two rules
        if len(self.rule_set) != 2: return False
        
        # If the first rule validates, then the second is required, too.
        if self.rule_set[0].validate(doc) == True:
            return self.rule_set[1].validate(doc)
        else:
            # The first rule did not validate, but doc is valid because condition means that we only fail
            #   if the first rule is passed and the second is failed.
            return True