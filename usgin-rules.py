import re, urllib2
from xmlvalidator import *

class MinimumRuleSet(list):
    def __init__(self):
        list.__init__(self)
        self.name = 'USGIN ISO Minimum Rules'
        
        rule = ExistsRule(name='Has File ID', 
                                        description='Checks that metadata hase a file identifier', 
                                        xpath='/gmd:MD_Metadata/gmd:fileIdentifier/gco:CharacterString')
        self.append(rule)
        
        # Language code list from http://www.loc.gov/standards/iso639-2/php/code_list.php
        languages = re.findall('<td scope="row">(.{3})</td>', urllib2.urlopen('http://www.loc.gov/standards/iso639-2/php/code_list.php').read())
        
        rule = ValueInListRule(name='Language Code is Valid',
                               description='Checks that Language Code is a valid ISO639-2 three-letter code',
                               xpath='/gmd:MD_Metadata/gmd:language/gco:CharacterString',
                               values=languages)
        self.append(rule)
        
        rule = ValueInListRule(name='CharacterSetCode codeList is Valid',
                               description='Checks that the CharacterSetCode attrribute codeList is correct',
                               xpath='/gmd:MD_Metadata/gmd:characterSet/gmd:MD_CharacterSetCode/@codeList',
                               values=['http://standards.iso.org/ittf/PubliclyAvailableStandards/ISO_19139_Schemas/resources/Codelist/gmxCodelists.xml#MD_CharacterSetCode'])
        self.append(rule)
        
        # Characters codes from Wolfgang's comments in the metadata template
        character_codes = ['ucs2', 'ucs4', 'utf7', 'utf8', 'utf16', '8859part1', '8859part2', '8859part3', '8859part4', '8859part5', '8859part6', '8859part7', '8859part8', '8859part9', '8859part10', '8859part11', '8859part13', '8859part14', '8859part15', '8859part16', 'jis', 'shiftJIS', 'eucJP', 'usAscii', 'ebcdic', 'eucKR', 'big5', 'GB2312']
        rule = ValueInListRule(name='CharacterSetCode codeListValue is Valid',
                               description='Checks that the CharacterSetCode attrribute codeListValue is correct',
                               xpath='/gmd:MD_Metadata/gmd:characterSet/gmd:MD_CharacterSetCode/@codeListValue',
                               values=character_codes)
        self.append(rule)
        
        rule = ValueInListRule(name='HierarchyLevel codeList is Valid',
                               description='Checks that the HierarchyLevel attrribute codeList is correct',
                               xpath='/gmd:MD_Metadata/gmd:hierarchyLevel/gmd:MD_ScopeCode/@codeList',
                               values=['http://standards.iso.org/ittf/PubliclyAvailableStandards/ISO_19139_Schemas/resources/Codelist/gmxCodelists.xml#MD_ScopeCode'])
        self.append(rule)
        
        # Characters codes from Wolfgang's comments in the metadata template
        hierarchy_codes = ['attribute', 'attributeType', 'collectionHardware', 'collectionSession', 'dataset', 'series', 'nonGeographicDataset', 'dimensionGroup', 'feature', 'featureType', 'propertyType', 'fieldSession', 'software', 'service', 'model', 'tile']
        rule = ValueInListRule(name='HierarchyLevel codeListValue is Valid',
                               description='Checks that the HierarchyLevel attrribute codeListValue is correct',
                               xpath='/gmd:MD_Metadata/gmd:hierarchyLevel/gmd:MD_ScopeCode/@codeListValue',
                               values=hierarchy_codes)
        self.append(rule)
        
        # HierarchyLevelNames list sounds priliminary, from Wolfgang's comments in the metadata template
        rule = ValueInListRule(name='HierarchyLevelName is Valid',
                               description='Checks that the HierarchyLevelName value is valid',
                               xpath='/gmd:MD_Metadata/gmd:hierarchyLevelName/gco:CharacterString',
                               values=['Dataset', 'Service'])
        self.append(rule)
        
        rule = AnyOfRule(name='Metadata Contact must have a named entity',
                         description='Checks that Metadata contact has at least one of: individualName, organisationName, poositionName',
                         xpaths=['/gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:individualName/gco:CharacterString',
                                 '/gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:organisationName/gco:CharacterString',
                                 '/gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:positionName/gco:CharacterString'])
        self.append(rule)
        
        rule = ContentMatchesExpressionRule(name='Metadata Contact must have an email address',
                                            description='Checks that Metadata Contact contains something that looks like an email address',
                                            xpath='/gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:electronicMailAddress/gco:CharacterString',
                                            expression='^.+@.+\..+$')
        self.append(rule)
        
        rule = ValueInListRule(name='Metadata Contact Role codeList is Valid',
                               description='Checks that the Metadata Contact Role has a valid codeList value',
                               xpath='/gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:role/gmd:CI_RoleCode/@codeList',
                               values=['http://standards.iso.org/ittf/PubliclyAvailableStandards/ISO_19139_Schemas/resources/Codelist/gmxCodelists.xml#CI_RoleCode'])
        self.append(rule)
        
        # Role codes are from Wolfgang's comments in the metadata template
        role_codes = ['resourceProvider', 'custodian', 'owner', 'user', 'distributor', 'originator', 'pointOfContact', 'principalInvestigator', 'processor', 'publisher', 'author']
        rule = ValueInListRule(name='Metadata Contact Role codeListValue is Valid',
                               description='Checks that the Metadata Contact Role has a valid codeListValue value',
                               xpath='/gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:role/gmd:CI_RoleCode/@codeListValue',
                               values=role_codes)
        self.append(rule)
        
        condition = ValueInListRule(name='Icon is labeled', 
                                   description='For use in conditional rule: Checks that an icon is present',
                                   xpath='/gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:onlineResource/gmd:CI_OnlineResource/gmd:name/gco:CharacterString',
                                   values=['icon'])
        neccessity = ContentMatchesExpressionRule(name='Where Icon is labeled, URL is required',
                                description='For user in conditional rule: When icon is present, a URL is required',
                                xpath='/gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:onlineResource/gmd:CI_OnlineResource/gmd:linkage/gmd:URL',
                                expression='^http://.+\..+$')
        conditional_rule = ConditionalRule(name='If Metadata Contact provides an Icon, a URL must be provided',
                                           description='Checks that where an Icon is listed, something looking like a URL is also provided',
                                           rule_set=[condition, neccessity])
        self.append(conditional_rule)
        
        rule = ContentMatchesExpressionRule(name='DateStamp looks like an ISO date',
                                            description='Checks that the DateStamp looks like an ISO-style datetime',
                                            xpath='/gmd:MD_Metadata/gmd:dateStamp/gco:DateTime',
                                            expression='^[1-2][0-9]{3}-[0-1][0-9]-[0-3][0-9]T[0-1][0-9]:[0-1][0-9]:[0-1][0-9]$')
        self.append(rule)
                               
filepath = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test-files', 'usgin-dataset-template-nocomments.xml')
result = record_is_valid(filepath, 'dataset', MinimumRuleSet())
if result == True: 
    print 'Hurrah!'
else:
    print 'Oh no!'