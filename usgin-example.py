from xmlvalidator import *

VALID_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test-files', 'usgin-dataset-template-nocomments.xml')

# Define a method that will be called when running this script
def example_validation():
    file = VALID_FILE # This is the file that is going to be validated
    metadata_type = 'dataset' # Either dataset or service
    validation_rules = list() # We'll populate the list with various rules
    
    # First, an ExistsRule. Checks whether or not there is content at a given XPath
    #  Syntax for building the rule: ExistsRule(name, description, xpath)
    xpath_exists_rule = ExistsRule(name='Has File ID', 
                                   description='Checks that metadata hase a file identifier', 
                                   xpath='/gmd:MD_Metadata/gmd:fileIdentifier/gco:CharacterString')
    
    validation_rules.append(xpath_exists_rule)
    
    # Next, a ValueInListRule. Checks whether or not the content of a given XPath is in a list you give it.
    #  Syntax for building the rule: ValueInListRule(name, description, xpath, values)
    value_in_list_rule = ValueInListRule(name='Language is valid',
                                         description='Checks that language identifier is appropriate',
                                         xpath='/gmd:MD_Metadata/gmd:language/gco:CharacterString',
                                         values=['eng', 'spa', 'fra'])
    validation_rules.append(value_in_list_rule)
    
    # AnyOfRule. Checks that at least one of the given XPaths have content
    #  Syntax for building the rule: AnyOfRule(name, description, xpaths)
    any_of_rule = AnyOfRule(name='Metadata Contact: Individual or Organization',
                            description='Checks that the Metadata Contact has one of individualName or organisationName',
                            xpaths=['//gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification',
                                    '//gmd:MD_Metadata/gmd:identificationInfo/srv:SV_ServiceIdentification'])
    validation_rules.append(any_of_rule)
    
    # OneOfRule is a special case for situations where you want one or the other XPath to exist, but more than one of them is an error.
    #  Syntax for building the rule: OneOfRule(name, description, xpaths)
    
    # ContentMatchesExpressionRule. Checks that the content of a given XPath matches a regular expression
    #  Syntax for building the rule: ContentMatchesExpressionRule(name, description, xpath, expression)
    match_content_rule = ContentMatchesExpressionRule(name='FileID is a GUID',
                                                      description="Checks that record's fileIdentifier is a GUID",
                                                      xpath='/gmd:MD_Metadata/gmd:fileIdentifier/gco:CharacterString',
                                                      expression='^[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12}$')
    validation_rules.append(match_content_rule)
    
    # After putting together a set of rules, I call record_is_valid to return a Boolean determination of if it passed the rules
    #  Syntax for validation is record_is_valid(filepath, record_type, rule_set)
    result, report = record_is_valid(file, validation_rules)
    if result == True: 
        print 'Hurrah!'
    else:
        for item in report:
            print item
    
# Now that my method is defined... lets run it!
example_validation()