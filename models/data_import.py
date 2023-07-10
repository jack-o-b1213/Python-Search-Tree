from dataclasses import dataclass

import pandas as pd


@dataclass
class ImportData:
    def __init__(self, filepath):
        self.directory = filepath
        self.filename = filepath.split("/")[-1]
        self.data_frame = pd.read_csv(filepath)
        self.surcharge = {
            'marketing': 1.1,
            'sales': 1.15,
            'development': 1.2,
            'operations': 0.85,
            'support': 0.95,
        }
        self.format_data()
        self.departments = self.data_frame.Department__c.unique()
        self.categories = self.data_frame.Category__c.unique()
        self.sub_categories = self.data_frame.Sub_Category__c.unique()
        self.types = self.data_frame.Type__c.unique()
        self.aggregate_function = ['total', 'max', 'min', 'avg']

    def format_data(self):
        for col in self.data_frame.columns:
            try:
                self.data_frame[col] = self.data_frame[col].str.lower().replace(' ', '_')
            except Exception as e:
                pass

        self.data_frame["Surcharge"] = self.data_frame["Department__c"].apply(lambda x: self.surcharge.get(x))
        self.data_frame["Fee"] = self.data_frame["Quantity__c"] * self.data_frame["Unit_Price__c"] * self.data_frame["Surcharge"]

    def extractQuery(self, raw_query):
        q_department, q_category, q_sub_category, q_fee_type, q_agg = '', '', '', '', 'total'
        for department in self.departments:
            if department in raw_query:
                q_department = department

        for category in self.categories:
            if category in raw_query:
                q_category = category

        for sub_category in self.sub_categories:
            if sub_category in raw_query:
                q_sub_category = sub_category

        for fee_type in self.types:
            if fee_type in raw_query:
                q_fee_type = fee_type

        for agg in self.aggregate_function:
            if agg in raw_query:
                q_agg = agg

        return q_department, q_category, q_sub_category, q_fee_type, q_agg

    def print_details(self):
        print("Rows: ", self.data_frame.shape[0])
        # print("Surcharges: ", self.surcharge)
