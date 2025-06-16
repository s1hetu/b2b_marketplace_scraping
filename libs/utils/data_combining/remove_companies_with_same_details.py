"""
Remove duplicate data
"""
from libs.utils.constants import DATA_COMPARISON_DICT
from libs.utils.log_services.logger import setup_logger

logger = setup_logger("remove_duplicates_with_same_details")


def generate_unique_field_data(data, field_name):
    """
    Generate unique field values from given data for given field based on count.
    :param data: The data to be checked from
    :param field_name: Name of the field to be checked
    :return: list of unique field values
    """
    unique_field_data = []
    all_field_data = [i.get(field_name) for i in data]
    logger.info(f"Total companies having {field_name}: {len(all_field_data)}")
    field_count_dict = {i: all_field_data.count(i) for i in all_field_data}
    for field, count in field_count_dict.items():
        if count == 1:
            unique_field_data.append(field)
    logger.info(f"Companies having no match based on {field_name}: {len(unique_field_data)}")
    return unique_field_data


def remove_companies_with_same_gst(data):
    """
    Remove companies that have same gst
    :param data: Data to check
    :return: list of companies having unique gst
    """
    unique_gsts = []
    companies = []
    for company in data:
        gst = company.get("gst")
        if gst:
            if gst not in unique_gsts:
                companies.append(company)
                unique_gsts.append(gst)
        else:
            companies.append(company)
    return companies


def remove_data_with_same_vendor_field(data, field):
    """
    Remove the companies that have same vendor id.
    If there are multiple companies with same vendor ID, select the
    one that has GST else the first match.
    :param data: Data to be checked
    :param field: Name of the field to check
    :return: list of companies having unique vendor id
    """
    unique_vendor_fields = generate_unique_field_data(data, field)
    unique_vendor_data = []
    duplicates= {}
    data_to_consider = []
    for each_company in data:
        field_value = each_company.get(field)
        if field_value in unique_vendor_fields:
            unique_vendor_data.append(each_company)
        else:
            if field_value not in duplicates:
                duplicates[field_value] = []
            duplicates[field_value].append(each_company)
    for companies in duplicates.values():
        gsts = [i.get("gst") for i in companies if i.get("gst")]
        if gsts:
            for cmpy in companies:
                gst = cmpy.get("gst")
                if gst:
                    company_to_add = cmpy
                    data_to_consider.append(company_to_add)
                    break
        else:
            company_to_add = companies[0]
            data_to_consider.append(company_to_add)
    unique_data = unique_vendor_data + data_to_consider
    logger.info(f"Unique companies based on {field}: {len(unique_data)}")
    return unique_data


def remove_data_with_same_details(combined_data):
    """
    Remove companies that have same details for:
    1. vendorId
    - Gather companies that have same vendor Id.
    - Find if any of them contains a GST number.
        If yes, consider that company, else select the 1st company.
    - New companies with unique vendor Ids further.
    2. GST
    - Gather companies that have same GST and pass them further,
    3. Companies with same name
    - Gather companies that have same name.
    - Create a dictionary containing name as key and companies as values in list.
    - Create a dictionary having source as key and companies as values in list from above dict values.
    - Check if companies have same values for fields defined in DATA_COMPARISON_DICT for each website source.
    - If they have matching details, remove that company.
    :param combined_data: Data to be checked
    :return: list of companies to be added to database
    """
    field = "vendorId"
    data = remove_data_with_same_vendor_field(combined_data, field)
    data = remove_companies_with_same_gst(data)
    unique_company_names = generate_unique_field_data(data, field)
    unique_company_name_data = []

    data_to_consider = []
    all_duplicate_companies = []
    all_duplicate_companies_id = []
    duplicate_company_instances = []
    duplicate_companies_data = {}

    for each_company in data:
        company_name = each_company.get("company")
        if company_name in unique_company_names:
            unique_company_name_data.append(each_company)
        else:
            if company_name not in duplicate_companies_data:
                duplicate_companies_data[company_name] = []
            duplicate_companies_data[company_name].append(each_company)

    for company_name, companies in duplicate_companies_data.items():
        website_source_map = {}
        all_duplicate_companies.extend(companies)
        for company in companies:
            all_duplicate_companies_id.extend([i.get("vendorId") for i in companies])

            source = company.get("source")
            if source not in website_source_map:
                website_source_map[source] = []
            website_source_map[source].append(company)

        for website, website_companies in website_source_map.items():
            if len(website_companies) > 1:
                comparison_fields = DATA_COMPARISON_DICT.get(website)
                comparison_dict = {"ids": [i.get("vendorId") for i in website_companies]}
                for each_field in comparison_fields:
                    comparison_dict[each_field] = [i.get(each_field) for i in website_companies]

                num_items = len(next(iter(comparison_dict.values())))
                if num_items > 1:
                    for i in range(num_items):
                        for j in range(i + 1, num_items):
                            same = all(comparison_dict[key][i] == comparison_dict[key][j]
                                       and comparison_dict[key][i] is not None
                                       for key in comparison_dict if key != "ids")
                            if same:
                                duplicate_company_instances.append(comparison_dict['ids'][j])

    for company in all_duplicate_companies:
        id_value = company.get("vendorId")
        if id_value not in duplicate_company_instances:
            data_to_consider.append(company)

    final_data = unique_company_name_data + data_to_consider
    logger.info(f"After removing companies with same details, : {len(final_data)}")
    return final_data
