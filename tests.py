import unittest, os
from lxml import etree
from xmlvalidator import *

VALID_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test-files', 'usgin-dataset-template-nocomments.xml')

class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.name = 'Testing Rule Name'
        self.desc = 'Testing Rule Description'
        self.valid_filepath = VALID_FILE
        self.invalid_filepath = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test-files', 'not-parsable.xml')
        self.rule_set = [ExistsRule(self.name, self.desc, '//gmd:MD_Metadata/gmd:fileIdentifier/gco:CharacterString')]
        
    def test_valid_input(self):
        # Make sure the valid test file exists
        self.assertTrue(os.path.exists(self.valid_filepath), 'Valid example file does not exist')
        
        # Make sure that the validator responds with TRUE when asked to parse the test file
        result, report = record_is_valid(self.valid_filepath, self.rule_set)
        self.assertTrue(result)
        self.assertEqual(len(report), 0)
        
        # Make sure that the validator responds with TRUE when asked to parse a valid test URL
        url = 'http://repository.azgs.az.gov/resources/metadata/testing/xmlvalidation/usgin-dataset-template.xml'
        result, report = record_is_valid(url, self.rule_set)
        self.assertTrue(result)
        self.assertEqual(len(report), 0)
        
        # Make sure that the validator responds with TRUE when asked to parse a valid test CSW Response
        url = 'http://catalog.usgin.org/geoportal/csw?request=GetRecordByID&service=CSW&Id=e2d27974-8b84-11df-ae28-4a34282d677f&ElementSetName=full&outputSchema=http://www.isotc211.org/2005/gmd'
        result, report = record_is_valid(url, self.rule_set)
        self.assertTrue(result)
        self.assertEqual(len(report), 0)
        
    def test_invalid_input(self):    
        # Make sure that the validator returns an appropriate exception when given bad inputs
        self.assertRaises(ValidationException, record_is_valid, filepath='/this/does/not/exist/')
        
        # Make sure that the validator returns an appropriate exception when asked to parse an invalid test URL
        url = 'http://repository.azgs.az.gov/resources/metadata/testing/xmlvalidation/thereisnothinghere.txt'
        self.assertRaises(ValidationException, record_is_valid, filepath=url)
        
    def test_invalid_file(self):
        # Make sure an appropriate exception is raised if the file is nonsense.
        self.assertRaises(ValidationException, record_is_valid, filepath=self.invalid_filepath)
    
    def test_fails_rule(self):
        # Make sure that validator fails if a rule set fails
        failed_rule_set = [ExistsRule(self.name, self.desc, '/invalid/xpath/expression')]
        result, report = record_is_valid(self.valid_filepath, failed_rule_set)
        self.assertFalse(result)
        
class RuleTests(unittest.TestCase):
    def setUp(self):
        self.name = 'Testing Rule Name'
        self.desc = 'Testing Rule Description'
        self.valid_doc = etree.parse(VALID_FILE)
        
    def test_abstract_rule(self):
        abs_rule = Rule(self.name, self.desc)
        self.assertEqual(abs_rule.name, self.name)
        self.assertEqual(abs_rule.description, self.desc)
        self.assertRaises(NotImplementedError, abs_rule.validate, doc=self.valid_doc)
        
    def test_exists_rule(self):
        xpath = '//gmd:MD_Metadata/gmd:fileIdentifier/gco:CharacterString'
        exists_rule = ExistsRule(self.name, self.desc, xpath)
        self.assertEqual(exists_rule.name, self.name)
        self.assertEqual(exists_rule.description, self.desc)
        self.assertEqual(exists_rule.xpath, xpath)
        
        self.assertTrue(exists_rule.validate(self.valid_doc), 'Valid XPath did not return True during ExistRule validation.')
        
        exists_rule = ExistsRule(self.name, self.desc, '/invalid/xpath/expression')
        self.assertFalse(exists_rule.validate(self.valid_doc), 'Invalid XPath did not return False during ExistRule validation.')
        
        exists_rule = ExistsRule(self.name, self.valid_doc, '/poorl:::y-formed/x!path/expression/')
        self.assertFalse(exists_rule.validate(self.valid_doc), 'Poorly-formed XPath expression did not return False during ExistsRule validation')
        
    def test_value_in_list_rule(self):
        xpath = '//gmd:MD_Metadata/gmd:language/gco:CharacterString'
        valid_list = ['eng', 'spa']
        in_list_rule = ValueInListRule(self.name, self.desc, xpath, valid_list)
        
        # Test basic attributes
        self.assertEqual(in_list_rule.name, self.name)
        self.assertEqual(in_list_rule.description, self.desc)
        self.assertEqual(in_list_rule.xpath, xpath)
        self.assertEqual(in_list_rule.values, valid_list)
        
        # Test invalid XPath
        in_list_rule = ValueInListRule(self.name, self.desc, '/invalid/xpath/expression', valid_list)
        self.assertFalse(in_list_rule.validate(self.valid_doc), 'Invalid xpath passes list validation.')
        # Test appropriate list
        in_list_rule = ValueInListRule(self.name, self.desc, xpath, valid_list)
        self.assertTrue(in_list_rule.validate(self.valid_doc), 'Valid document does not pass list validation.')
        # Test inappropriate list as proxy for invalid document content
        in_list_rule = ValueInListRule(self.name, self.desc, xpath, ['pants', 'shoes'])
        self.assertFalse(in_list_rule.validate(self.valid_doc), 'Invalid document passes list validation.')
        # Test when xpath asks for a specific attribute
        attr_xpath = '//gmd:MD_Metadata/gmd:characterSet/gmd:MD_CharacterSetCode/@codeListValue'
        in_list_rule = ValueInListRule(self.name, self.desc, attr_xpath, ['utf8'])
        self.assertTrue(in_list_rule.validate(self.valid_doc), 'Valid attribute XPath does not pass validation')
        
    def test_one_of_these_rule(self):
        valid_xpaths = ['//gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:individualName/gco:CharacterString']    
        valid_xpaths.append('//gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:organisationName/gco:CharacterString')
        one_of_rule = AnyOfRule(self.name, self.desc, valid_xpaths)
        
        # Test basic attributes
        self.assertEqual(one_of_rule.name, self.name)
        self.assertEqual(one_of_rule.description, self.desc)
        self.assertEqual(one_of_rule.xpaths, valid_xpaths)
        
        # Test for success: Both xpaths are present
        self.assertTrue(one_of_rule.validate(self.valid_doc), 'Valid document did not validate against a valid AnyOf Rule.')
        # Test for success: One of two xpaths are present
        valid_xpaths = ['//gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:individualName/gco:CharacterString']
        valid_xpaths.append('/hibbity/haw/haw')
        one_of_rule = AnyOfRule(self.name, self.desc, valid_xpaths)
        self.assertTrue(one_of_rule.validate(self.valid_doc), 'Valid document did not validate against a valid AnyOf Rule.')
        # Test for failure: Neither XPath is present, one is bogus.
        xpaths = ['/hee/hee/hibbity/hee/']
        xpaths.append('/hibbity/haw/haw')
        one_of_rule = AnyOfRule(self.name, self.desc, xpaths)
        self.assertFalse(one_of_rule.validate(self.valid_doc), 'Valid document did not fail validation against an invalid AnyOf Rule.')
        
        # Test context success
        context_doc = etree.parse(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test-files', 'context-test.xml'))
        context = '//thing'
        xpaths = ['/one', '/two']
        one_of_rule = AnyOfRule(self.name, self.desc, xpaths, context)
        self.assertTrue(one_of_rule.validate(context_doc))
        
        # Test context failure
        xpaths = ['/three']
        one_of_rule = AnyOfRule(self.name, self.desc, xpaths, context)
        self.assertFalse(one_of_rule.validate(context_doc))
        
    def test_either_or_rule(self):
        xpaths = ['/clothing/footwear/sneakers', '/clothing/footwear/hightops']
        file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test-files', 'either-or-test.xml')
        one_of_doc = etree.parse(file)
        either_or_rule = OneOfRule(self.name, self.desc, xpaths)
        
        # Test basic attributes
        self.assertEqual(either_or_rule.name, self.name)
        self.assertEqual(either_or_rule.description, self.desc)
        self.assertEqual(either_or_rule.xpaths, xpaths)    
        
        # Test for success
        self.assertTrue(either_or_rule.validate(one_of_doc), 'Valid document did not validate against a valid OneOf Rule.')
        # Test for failure: both exist
        xpaths = ['/clothing/footwear/sneakers','/clothing/leggings/pants']
        either_or_rule = OneOfRule(self.name, self.desc, xpaths)
        self.assertFalse(either_or_rule.validate(one_of_doc), 'Valid document did validated against an invalid OneOf Rule.')
        # Test for failure: Neither XPath is present, one is bogus.
        xpaths = ['/hibbity/haw/haw','/hee/hee/hibbity/hee/']
        either_or_rule = OneOfRule(self.name, self.desc, xpaths)
        self.assertFalse(either_or_rule.validate(one_of_doc), 'Valid document did validated against an invalid OneOf Rule.')
    
    def test_content_matches_rule(self):
        xpath = '//gmd:MD_Metadata/gmd:fileIdentifier/gco:CharacterString'
        valid_expression = '^[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12}$'
        matches_rule = ContentMatchesExpressionRule(self.name, self.desc, xpath, valid_expression)    
        
        # Test basic attributes
        self.assertEqual(matches_rule.name, self.name)
        self.assertEqual(matches_rule.description, self.desc)
        self.assertEqual(matches_rule.xpath, xpath)
        self.assertEqual(matches_rule.expression, valid_expression)
        
        # Test for success
        self.assertTrue(matches_rule.validate(self.valid_doc), 'Valid document did not validate against a valid ContentMatchesExpression Rule')
        
        # Test for failure: unmatching RE 
        expression = '^DoesNotMatch$'
        matches_rule = ContentMatchesExpressionRule(self.name, self.desc, xpath, expression)
        self.assertFalse(matches_rule.validate(self.valid_doc), 'Valid document validated against a ContentMatchesExpression Rule that should not match')
        
        # Test for failure: invalid RE
        expression ='(()..!'
        matches_rule = ContentMatchesExpressionRule(self.name, self.desc, xpath, expression)
        self.assertFalse(matches_rule.validate(self.valid_doc), 'Valid document validated against a ContentMatchesExpression Rule with an invalid expression')
        
        # Test for failure: invalid XPath
        xpath = '/poorl:::y-formed/x!path/expression/'
        matches_rule = ContentMatchesExpressionRule(self.name, self.desc, xpath, valid_expression)
        self.assertFalse(matches_rule.validate(self.valid_doc), 'Valid document validated against a ContentMatchesExpression Rule with an invalid xpath')
        
        # Test for failure: expression matches only part of the content
        xpath = '//gmd:MD_Metadata/gmd:fileIdentifier/gco:CharacterString'
        expression = '00C02E67-F1ED'
        matches_rule = ContentMatchesExpressionRule(self.name, self.desc, xpath, expression)
        self.assertFalse(matches_rule.validate(self.valid_doc), 'Valid document validated against a ContentMatchesExpression Rule with an expression that does not match the complete content of the node')
    
    def test_conditional_rule(self):
        xpath_one = '//gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:onlineResource/gmd:CI_OnlineResource/gmd:name/gco:CharacterString'
        xpath_two = '//gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:onlineResource/gmd:CI_OnlineResource/gmd:linkage/gmd:URL'
        rule_one = ValueInListRule(self.name, self.desc, xpath_one, ['icon'])
        rule_two = ExistsRule(self.name, self.desc, xpath_two)
        conditional_rule = ConditionalRule(self.name, self.desc, [rule_one, rule_two])
        
        # Test for success
        self.assertTrue(conditional_rule.validate(self.valid_doc), 'Valid document did not validate against a Conditional Rule with a valid rule_set')
        
        # Test for failure: Wrong number of rules given
        conditional_rule = ConditionalRule(self.name, self.desc, ['one', 'two', 'three'])
        self.assertFalse(conditional_rule.validate(self.valid_doc), 'Valid document validated against a ConditionalRule with the incorrect number of rules given')
    
    def test_valid_url_rule(self):
        xpath = '//gmd:URL'
        url_rule = ValidUrlRule(self.name, self.desc, xpath)
        
        # Test for success
        self.assertTrue(url_rule.validate(self.valid_doc), 'Valid document did not pass a URL is valid rule.')
            
    def tearDown(self):
        #self.valid_doc.freeDoc()
        pass