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
        
        # HierarchyLevelNames list sounds preliminary, from Wolfgang's comments in the metadata template
        rule = ValueInListRule(name='HierarchyLevelName is Valid',
                               description='Checks that the HierarchyLevelName value is valid',
                               xpath='/gmd:MD_Metadata/gmd:hierarchyLevelName/gco:CharacterString',
                               values=['Dataset', 'Service'])
        self.append(rule)
        
        rule = AnyOfRule(name='Metadata Contact must have a named entity',
                         description='Checks that Metadata contact has at least one of: individualName, organisationName, postionName',
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
                                description='For use in conditional rule: When icon is present, a URL is required',
                                xpath='/gmd:MD_Metadata/gmd:contact/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:onlineResource/gmd:CI_OnlineResource/gmd:linkage/gmd:URL',
                                expression='^http://.+\..+$')
        conditional_rule = ConditionalRule(name='If Metadata Contact provides an Icon, a URL must be provided',
                                           description='Checks that where an Icon is listed, something looking like a URL is also provided',
                                           rule_set=[condition, neccessity])
        self.append(conditional_rule)
        
        rule = ContentMatchesExpressionRule(name='DateStamp looks like an ISO date',
                                            description='Checks that the DateStamp looks like an ISO-style datetime',
                                            xpath='/gmd:MD_Metadata/gmd:dateStamp/gco:DateTime',
                                            expression='^[1-2][0-9]{3}-[0-1][0-9]-[0-3][0-9]T[0-1][0-9]:[0-6][0-9]:[0-6][0-9]$')
        self.append(rule)
        
        rule = ValueInListRule(name='Metadata Standard Name is identified',
                               description='Checks that the Metadata Standard Name identifies this record as ISO_NAP_USGIN',
                               xpath='/gmd:MD_Metadata/gmd:metadataStandardName/gco:CharacterString',
                               values=['ISO-NAP-USGIN'])
        self.append(rule)
        
        rule = ExistsRule(name='Metadata Standard Version is identified',
                          description='Checks that the Metadata Standard Version is identified',
                          xpath='/gmd:MD_Metadata/gmd:metadataStandardVersion/gco:CharacterString')
        
        rule = AnyOfRule(name='Resource Identification is Required',
                         description='At least one of MD_DataIdentification (dataset, dataset series) or SV_ServiceIdentification (service) is required',
                         xpaths=['/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification',
                                 '/gmd:MD_Metadata/gmd:identificationInfo/gmd:SV_ServiceIdentification'])
        self.append(rule)
        
        dataset_condition = ExistsRule(name='Record is a Dataset', 
                               description='For use in conditional rule: Checks that MD_DataIdentification is present',
                               xpath='/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification')
        neccessity = ExistsRule(name='Dataset requires CI_Citation',
                                description='For use in conditional rule: Datasets require CI_Citation',
                                xpath='/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation')
        rule = ConditionalRule(name='Datasets must contain a CI_Citation',
                               description='Checks that dataset records contain a CI_Citation',
                               rule_set=[dataset_condition, neccessity])
        self.append(rule)
        
        neccessity = ExistsRule(name='Dataset CI_Citation Requires a Title',
                                description='For use in conditional rule: Dataset CI_Citations require a title',
                                xpath='/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString')
        rule = ConditionalRule(name='Dataset CI_Citation Requires a Title',
                               description='Checks that Dataset CI_Citations have a title',
                               rule_set=[dataset_condition, neccessity])
        self.append(rule)
        
        neccessity = ValueInListRule(name='Dataset CI_Citation DateTypeCode codeList is valid',
                                    description='For use in conditional rule: Dataset CI_Citations DateTypeCode codeList must be defined',
                                    xpath='/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:date/gmd:CI_Date/gmd:dateType/gmd:CI_DateTypeCode/@codeList',
                                    values=['http://standards.iso.org/ittf/PubliclyAvailableStandards/ISO_19139_Schemas/resources/Codelist/gmxCodelists.xml#CI_DateTypeCode'])
        rule = ConditionalRule(name='Dataset CI_Citation DateTypeCode codeList is valid',
                               description='Dataset CI_Citations DateTypeCode codeList is correct',
                               rule_set=[dataset_condition, neccessity])
        self.append(rule)
        
        neccessity = ValueInListRule(name='Dataset CI_Citation DateTypeCode codeListValue is valid',
                                    description='For use in conditional rule: Dataset CI_Citations DateTypeCode codeListValue must be defined',
                                    xpath='/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:date/gmd:CI_Date/gmd:dateType/gmd:CI_DateTypeCode/@codeListValue',
                                    values=['creation', 'publication', 'revision'])
        rule = ConditionalRule(name='Dataset CI_Citation DateTypeCode codeListValue is valid',
                               description='Dataset CI_Citations DateTypeCode codeListValue is correct',
                               rule_set=[dataset_condition, neccessity])
        self.append(rule)
        
        neccessity = ContentMatchesExpressionRule(name='Dataset CI_Citation DateTime is Valid',
                                    description='For use in conditional rule: Dataset CI_Citations DateTime must be an ISO 8601 formatted string',
                                    xpath='/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:date/gmd:CI_Date/gmd:date/gco:DateTime',
                                    expression='^[1-2][0-9]{3}-[0-1][0-9]-[0-3][0-9]T[0-1][0-9]:[0-6][0-9]:[0-6][0-9]$')
        rule = ConditionalRule(name='Dataset CI_Citation DateTime Looks Like ISO',
                               description='Dataset CI_Citations DateTime must be an ISO 8601 formatted string',
                               rule_set=[dataset_condition, neccessity])
        self.append(rule)
        
        neccessity = AnyOfRule(name='Intellectual Contact must have a named entity',
                         description='For use in conditional rule: Checks that Intellectual contact has at least one of: individualName, organisationName, postionName',
                         xpaths=['/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:citedResponsibleParty/gmd:CI_ResponsibleParty/gmd:individualName/gco:CharacterString',
                                 '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:citedResponsibleParty/gmd:CI_ResponsibleParty/gmd:organisationName/gco:CharacterString',
                                 '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:citedResponsibleParty/gmd:CI_ResponsibleParty/gmd:positionName/gco:CharacterString'])
        rule = ConditionalRule(name='Dataset Intellectual Contact must have a named entity',
                               description='For a Dataset: Checks that Resource contact has at least one of: individualName, organisationName, postionName',
                               rule_set=[dataset_condition, neccessity])
        self.append(rule)
        
        neccessity = AnyOfRule(name='Intellectual Contact must have a some Contact Info',
                         description='For use in conditional rule: Checks that Intellectual contact has at least one of: phone, deliveryPoint, email',
                         xpaths=['/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:citedResponsibleParty/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:phone/gmd:CI_Telephone/gmd:voice/gco:CharacterString',
                                 '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:citedResponsibleParty/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:deliveryPoint/gco:CharacterString',
                                 '/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:citedResponsibleParty/gmd:CI_ResponsibleParty/gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd:electronicMailAddress/gco:CharacterString'])
        rule = ConditionalRule(name='Dataset Intellectual Contact must have a some Contact Info',
                               description='For a Dataset: Checks that Resource contact has at least one of: phone, deliveryPoint, email',
                               rule_set=[dataset_condition, neccessity])
        self.append(rule)
        
        neccessity = ValueInListRule(name='Dataset CI_Citation RoleCode codeList is valid',
                                    description='For use in conditional rule: Dataset CI_Citations RoleCode codeList is valid',
                                    xpath='/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:citedResponsibleParty/gmd:CI_ResponsibleParty/gmd:role/gmd:CI_RoleCode/@codeList',
                                    values=['http://standards.iso.org/ittf/PubliclyAvailableStandards/ISO_19139_Schemas/resources/Codelist/gmxCodelists.xml#CI_RoleCode'])
        rule = ConditionalRule(name='Dataset CI_Citation RoleCode codeList is valid',
                               description='For a Dataset: Checks that CI_Citations RoleCode codeList is valid',
                               rule_set=[dataset_condition, neccessity])
        self.append(rule)
        
        neccessity = ValueInListRule(name='Dataset CI_Citation RoleCode codeListValue is valid',
                                    description='For use in conditional rule: Dataset CI_Citations RoleCode codeListValue is valid',
                                    xpath='/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:citedResponsibleParty/gmd:CI_ResponsibleParty/gmd:role/gmd:CI_RoleCode/@codeListValue',
                                    values=role_codes)
        rule = ConditionalRule(name='Dataset CI_Citation RoleCode codeLisValue is valid',
                               description='For a Dataset: Checks that CI_Citations RoleCode codeListValue is valid',
                               rule_set=[dataset_condition, neccessity])
        self.append(rule)
        
        neccessity = ExistsRule(name='Dataset has an Abstract',
                                description='For use in conditional rule: Dataset must have an abstract',
                                xpath='/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:abstract/gco:CharacterString')
        rule = ConditionalRule(name='Dataset has an Abstract',
                               description='For a Dataset: Checks that an abstract is present',
                               rule_set=[dataset_condition, neccessity])
        self.append(rule)
        
        neccessity = ValueInListRule(name='Dataset Status codeList is valid',
                                    description='For use in conditional rule: Dataset Status codeList is valid',
                                    xpath='/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:status/gmd:MD_ProgressCode/@codeList',
                                    values=['http://standards.iso.org/ittf/PubliclyAvailableStandards/ISO_19139_Schemas/resources/Codelist/gmxCodelists.xml#MD_ProgressCode'])
        rule = ConditionalRule(name='Dataset Status codeList is valid',
                               description='For a Dataset: Checks that Status codeList is valid',
                               rule_set=[dataset_condition, neccessity])
        self.append(rule)
        
        # Progress codes are from Wolfgang's comments in the metadata template
        progress_codes =['completed', 'historicalArchive', 'obsolete', 'onGoing', 'planned', 'required', 'underDevelopment']
        neccessity = ValueInListRule(name='Dataset Status codeListValue is valid',
                                    description='For use in conditional rule: Dataset Status codeListValue is valid',
                                    xpath='/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:status/gmd:MD_ProgressCode/@codeListValue',
                                    values=progress_codes)
        rule = ConditionalRule(name='Dataset Status codeListValue is valid',
                               description='For a Dataset: Checks that Status codeListValue is valid',
                               rule_set=[dataset_condition, neccessity])
        self.append(rule)
        
        neccessity = ValueInListRule(name='Dataset Resource Language Code is Valid',
                               description='For use in conditional: Checks that Dataset Resource Language Code is a valid ISO639-2 three-letter code',
                               xpath='/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:language/gco:CharacterString',
                               values=languages)
        rule = ConditionalRule(name='Dataset Resource Language Code is Valid',
                               description='For a Dataset: Checks that Resource Language Code is a valid ISO639-2 three-letter code',
                               rule_set=[dataset_condition, neccessity])
        self.append(rule)
        
        dist_condition = ExistsRule(name='Distribution Information is Included', 
                               description='For use in conditional rule: Checks MD_Distribution is present',
                               xpath='/gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution')
        neccessity = ExistsRule(name='Distribution Format is Included',
                                description='For use in conditional rule: When distribution information is present, a distribution format is required',
                                xpath='/gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:distributionFormat')
        rule = ConditionalRule(name='Distribution Information requires Distribution Format',
                                           description='Checks that when distribution information is present, a distribution format is present',
                                           rule_set=[dist_condition, neccessity])
        self.append(rule)
        
        neccessity = ExistsRule(name='Transfer Options are Included',
                                description='For use in conditional rule: When distribution information is present, a transfer options are required',
                                xpath='/gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:transferOptions')
        rule = ConditionalRule(name='Distribution Information requires Transfer Options',
                                           description='Checks that when distribution information is present, transfer options are present',
                                           rule_set=[dist_condition, neccessity])
        self.append(rule)
        
        neccessity = AnyOfRule(name='Distributor has a named Entity',
                                description='For use in conditional rule: When distribution information is present, a distributor is required with a named entity',
                                xpaths=['/gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:distributor/gmd:MD_Distributor/gmd:distributorContact/gmd:CI_ResponsibleParty/gmd:individualName',
                                        '/gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:distributor/gmd:MD_Distributor/gmd:distributorContact/gmd:CI_ResponsibleParty/gmd:organisationName',
                                        '/gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:distributor/gmd:MD_Distributor/gmd:distributorContact/gmd:CI_ResponsibleParty/gmd:positionName'])
        rule = ConditionalRule(name='Distribution Information requires Distributor with Named Entity',
                                           description='Checks that when distribution information is present, a distributor is required with a named entity',
                                           rule_set=[dist_condition, neccessity])
        self.append(rule)
        
        neccessity = ValueInListRule(name='Distributor RoleCode codeList is valid',
                                    description='For use in conditional rule: Distributor RoleCode codeList is valid',
                                    xpath='/gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:distributor/gmd:MD_Distributor/gmd:distributorContact/gmd:CI_ResponsibleParty/gmd:role/gmd:CI_RoleCode/@codeList',
                                    values=['http://standards.iso.org/ittf/PubliclyAvailableStandards/ISO_19139_Schemas/resources/Codelist/gmxCodelists.xml#CI_RoleCode'])
        rule = ConditionalRule(name='Distributor RoleCode codeList is valid',
                               description='Where Distribution info is present: Checks that distributor RoleCode codeList is valid',
                               rule_set=[dist_condition, neccessity])
        self.append(rule)
        
        neccessity = ValueInListRule(name='Distributor RoleCode codeListValue is valid',
                                    description='For use in conditional rule: Distributor RoleCode codeListValue is valid',
                                    xpath='/gmd:MD_Metadata/gmd:distributionInfo/gmd:MD_Distribution/gmd:distributor/gmd:MD_Distributor/gmd:distributorContact/gmd:CI_ResponsibleParty/gmd:role/gmd:CI_RoleCode/@codeListValue',
                                    values=role_codes)
        rule = ConditionalRule(name='Distributor RoleCode codeList is valid',
                               description='Where Distribution info is present: Checks that distributor RoleCode codeListValue is valid',
                               rule_set=[dist_condition, neccessity])
        self.append(rule)
                               
filepath = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test-files', 'usgin-dataset-template.xml')
result, report = record_is_valid(filepath, 'dataset', MinimumRuleSet())
if result == True: 
    print 'Hurrah!'
else:
    print report