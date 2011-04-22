import os, re, datetime, urllib2
from lxml import etree
from urllib2 import URLError, HTTPError

ns = {'gmd': 'http://www.isotc211.org/2005/gmd',
      'srv': 'http://www.isotc211.org/2005/srv',
      'gco': 'http://www.isotc211.org/2005/gco',
      'gml': 'http://www.opengis.net/gml',
      'xlink': 'http://www.w3.org/1999/xlink',
      'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}

class ValidationException(Exception):
    def __init__(self, message='Validation problem'):
        self.msg = message

class ValidationReport(list):
    def __init__(self):
        list.__init__(self)
        self.run_time = datetime.datetime.now()
        
    def report_as_string(self):
        return '\n\n'.join(self)
    
def url_is_valid(url):
    req = urllib2.Request(url)
    result = True
    response = ''
    
    try:
        content = urllib2.urlopen(req)
    except HTTPError, ex:
        response = 'Invalid URL.' + str(ex.code)
        result = False
    except URLError, ex:
        response = 'Invalid URL. ' + str(ex.reason)
        result = False
    except ValueError, ex:
        response = 'Invalid URL Format: ' + url
        result = False
    
    return result, response
                
def record_is_valid(filepath, rule_set=None):
    # First, is it a valid file?
    if os.path.exists(filepath):
        content = filepath
        
    else:
        valid, response = url_is_valid(filepath)
        if not valid:
            raise ValidationException(response)
        else:
            req = urllib2.Request(filepath)
            content = urllib2.urlopen(req)
            
    # Insure the document is valid: Must be parse-able by lxml
    try:
        doc = etree.parse(content)
    except Exception as (ex):
        raise ValidationException(ex.msg)
    
    # Initiate a report
    report = ValidationReport()
    
    # Check each Rule
    result = True
    for rule in rule_set:
        if rule.validate(doc) == False: 
            result = False
            report.append('FAILED: ' + rule.name + ' - ' + rule.description)
            
    # Validation has occurred. Return the result and report
    return result, report

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
        try:
            result = doc.xpath(self.xpath, namespaces=ns)
        except Exception as (ex):
            return False
        
        if len(result) > 0:
            result = True
        else:
            result = False
            
        # Finished. Cleanup the context and return True
        return result

class ValidUrlRule(Rule):
    def __init__(self, name, description, xpath):
        Rule.__init__(self, name, description)
        self.xpath = xpath
        
    def validate(self, doc):
        # Check that the XPath exists using an ExistsRule
        exists_rule = ExistsRule(self.name, self.description, self.xpath)
        if exists_rule.validate(doc) == False: return False
        
        nodes = doc.xpath(self.xpath, namespaces=ns)
        for node in nodes:
            # XPath evaluation will either return an element with a text attribute, or a string straight-up
            if hasattr(node, 'text'):
                result, response = url_is_valid(node.text)
            else:
                result, response = url_is_valid(node)
            
            if result == False: return False    
        
        return True
        
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
        nodes = doc.xpath(self.xpath, namespaces=ns)
        
        # Loop through them and check the values
        result = True
        for node in nodes:
            # XPath evaluation will either return an element with a text attribute, or a string straight-up
            if hasattr(node, 'text'):
                if node.text not in self.values: result = False
            else:
                if node not in self.values: result = False
        
        # Finished
        return result
    
class AnyOfRule(Rule):
    def __init__(self, name, description, xpaths, context='/'):
        Rule.__init__(self, name, description)
        self.xpaths = xpaths
        self.context = context
        
    def validate(self, doc):
        try:
            if self.context == '/':
                nodes = doc.xpath(doc.getpath(doc.getroot()), namespaces=ns)
            else:
                nodes = doc.xpath(self.context, namespaces=ns)
        except Exception as (ex):
            return False
        
        for node in nodes:
            # For each XPath in xpaths, check that at least one exists using ExistsRules
            count = 0
            for xpath in self.xpaths:
                if not xpath.startswith('//'):
                    if not xpath.startswith(doc.getpath(node)):
                        xpath = doc.getpath(node) + xpath
                        
                exists_rule = ExistsRule(self.name, self.description, xpath)
                if exists_rule.validate(doc) == True: count = count + 1
                
            if count < 1: 
                return False
            
        return True
        
        
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
        nodes = doc.xpath(self.xpath, namespaces=ns)
        
        result = True
        for node in nodes:
            if hasattr(node, 'text'):
                content = node.text
            else:
                content = node
                
            try:
                match = re.match(self.expression, content)
                # If there was no match, match will be None
                if match == None: result = False
                # If the regular expression had capture groups in it, there will be more than one. This indicates a poorly formed expression for this purpose.
                if len(match.groups()) > 1: result = False
                # If these lengths are different, then the RegEx only matched PART of the node's content.
                if len(match.group(0)) != len(content): result = False
            except:
                # Likely caused by an invalid expression
                return False
            
        # Finished
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