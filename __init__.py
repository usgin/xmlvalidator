import os, uuid, glob, urllib2, csv
from StringIO import StringIO
from lxml import etree
from xmlvalidator import *
from utils.validcsv import validate, validate_fields, validate_row
from utils.readcsv import csv_to_dict_reader
from utils.writecsv import new_csv_file
from utils.csvtoxml import transform_valid_csv, CURRENT_XSLT_PATH, transform_valid_row
from usginrules import UsginMinRules as minimum_rules

'''
rule_string = urllib2.urlopen('http://services.usgin.org/validation/ruleset/1/list/').read()
exec rule_string
minimum_rules = UsginMinRules()
'''

def get_usgin_rules():
    try:
        rule_string = urllib2.urlopen('http://services.usgin.org/validation/ruleset/1/list/').read()
        exec rule_string
        return UsginMinRules()
    except:
        from usginrules import UsginMinRules
        return UsginMinRules()

minimum_rules = get_usgin_rules()

ns = {'gmd': 'http://www.isotc211.org/2005/gmd',
      'srv': 'http://www.isotc211.org/2005/srv',
      'gco': 'http://www.isotc211.org/2005/gco',
      'gml': 'http://www.opengis.net/gml',
      'xlink': 'http://www.w3.org/1999/xlink',
      'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}

def validatecsv(filepath):
    reader = csv_to_dict_reader(filepath)
    return validate(reader)

def save_metadata(record_to_save, place_to_save_it, index):
    # Record should have a file identifier - find it.
    try:
        file_ish = StringIO(record_to_save)
        record = etree.parse(file_ish)
        fileId = record.xpath('//gmd:fileIdentifier/gco:CharacterString', namespaces=ns)[0]
    except Exception, ex:
        raise ex
    
    # This should really be handled at the validation level. By this point should have fileIdentifier
    #if fileId.text == None:
    #    id = str(uuid.uuid4())
    #else:
    #    id = fileId.text
    try:    
        filepath = os.path.join(place_to_save_it, fileId.text + '.xml')
        file = open(filepath, 'w')
    except IOError:
        filepath = os.path.join(place_to_save_it, str(index) + '.xml')
        file = open(filepath, 'w')
    try:
        file.write(record_to_save)
        file.close()
    except Exception, ex:
        raise ex
    
    return validate_output(filepath), filepath
    
def validate_output(filepath):
    try:
        result, report = record_is_valid(filepath, minimum_rules)
    except ValidationException, ex:
        raise ex
    if result == False:
        print 'FAILED VALIDATION: ' + os.path.split(filepath)[1]
        for item in report: print item
    else:
        print 'PASSED VALIDATION: ' + os.path.split(filepath)[1]
        
    return result

def move_valid_xml(filepath):
    # Move the file into the "valid" directory
    folder, name = os.path.split(filepath)
    valid_folder_path = os.path.join(os.path.split(folder)[0], 'valid-xml')
    if not os.path.exists(valid_folder_path): os.makedirs(valid_folder_path)
    new_file_path = os.path.join(valid_folder_path, name)
    os.rename(filepath, new_file_path)
    
def transformcsv(csv_filepath, output_folder_path):
    # Covert CSV to DictReader
    reader = csv_to_dict_reader(csv_filepath)
    
    # Check for valid fields
    result, report = validate_fields(reader)
    # If field validation failed, do not proceed
    if result == False:
        for item in report:
            print item
            return report
    
    # Setup output CSV files: One for valid rows, one for invalid rows
    fields = reader.fieldnames
    if not os.path.exists(output_folder_path): os.makedirs(output_folder_path)
    invalid_writer = new_csv_file(output_folder_path, 'invalid-rows', fields)
    valid_writer = new_csv_file(output_folder_path, 'valid-rows', fields)
    
    # Begin looping through rows
    final_report = list()
    for index, row in enumerate(reader):
        row_result, row_report = validate_row(index, row, fields)
        if row_result == False:
            # Row was not valid. Write to invalid CSV file.
            invalid_writer.writerow(row)
        else:
            # Row was valid. Write to valid CSV file.
            valid_writer.writerow(row)
            
            # Create XML for this row. save_metadata method automatically validates the saved file.
            invalid_xml_path = os.path.join(output_folder_path, 'invalid-xml')
            if not os.path.exists(invalid_xml_path): os.makedirs(invalid_xml_path)
            xml_is_valid, xml_filepath = save_metadata(transform_valid_row(row), invalid_xml_path, index)
            
            # Move the XML to the "valid" folder if it was...
            if xml_is_valid:
                move_valid_xml(xml_filepath)
                
        # Either way, append the report items to the final report
        for item in row_report:
            final_report.append(item)
        
    # Print the report - No Warnings
    for item in final_report:
        if not item.startswith('WARNING'): print item
        
    return final_report