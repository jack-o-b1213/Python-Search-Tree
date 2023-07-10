import unittest
from fees_hierarchy import generateResult, formatQuery, calculateFees
from models.data_import import ImportData
from models.tree import buildHierarchy

test_data = ImportData('data/raw_fees.csv')
hierarchy = buildHierarchy(test_data)


def generate_output(raw_query):
    raw_query = raw_query.lower()
    q_department, q_category, q_sub_category, q_fee_type, q_agg = test_data.extractQuery(raw_query)
    query = f"{q_department}:{q_category}:{q_sub_category}:{q_fee_type}".replace(' ', '_').split(':')
    steps = formatQuery(query)
    total_fees = calculateFees(hierarchy, steps, q_department, q_agg)
    return total_fees


class HierarchyFeesTestCase(unittest.TestCase):

    def test_de_qa_cat1(self):
        total_fees = generate_output('What are the total Cat1 fees within Quality Assurance Category of the '
                                     'Development department?')
        self.assertEqual(total_fees, 110212)

    def test_hr_op(self):
        total_fees = generate_output('What are the total fees for the Human Resources category of the Operations '
                                     'department?')
        self.assertEqual(total_fees, 229041)

    def test_blank(self):
        total_fees = generate_output('')
        self.assertEqual(total_fees, 'Invalid Query')

    def test_wrong_department(self):
        total_fees = generate_output('What are the total fees for the Coding category of the Operations '
                                     'department?')
        self.assertEqual(total_fees, 'Invalid Query')

    def test_entire_department(self):
        total_fees = generate_output('What are the total fees for the Operations department?')
        test_fee = int(
            test_data.data_frame.loc[test_data.data_frame['Department__c'] == 'operations']['Fee'].sum())
        self.assertEqual(total_fees, test_fee)

    def test_entire_category(self):
        total_fees = generate_output('What are the total fees for the Coding category?')
        test_fee = int(
            test_data.data_frame.loc[test_data.data_frame['Category__c'] == 'coding']['Fee'].sum())
        self.assertEqual(total_fees, test_fee)

    def test_entire_sub_category(self):
        total_fees = generate_output('What are the total fees for the Cat1 sub category of fees?')
        test_fee = test_data.data_frame.loc[test_data.data_frame['Sub_Category__c'] == 'cat1']

        test_fee_m = (test_fee.loc[test_fee['Department__c'] == 'marketing']['Fee'].sum())
        test_fee_s = (test_fee.loc[test_fee['Department__c'] == 'sales']['Fee'].sum())
        test_fee_d = (test_fee.loc[test_fee['Department__c'] == 'development']['Fee'].sum())
        test_fee_o = (test_fee.loc[test_fee['Department__c'] == 'operations']['Fee'].sum())
        test_fee_ss = (test_fee.loc[test_fee['Department__c'] == 'support']['Fee'].sum())

        self.assertEqual(total_fees, int(sum([test_fee_m, test_fee_s, test_fee_d, test_fee_o, test_fee_ss])))

    def test_entire_fee_type(self):
        total_fees = generate_output('What are the total fees for the TypeA fees?')
        test_fee = test_data.data_frame.loc[test_data.data_frame['Type__c'] == 'typea']

        test_fee_m = (test_fee.loc[test_fee['Department__c'] == 'marketing']['Fee'].sum())
        test_fee_s = (test_fee.loc[test_fee['Department__c'] == 'sales']['Fee'].sum())
        test_fee_d = (test_fee.loc[test_fee['Department__c'] == 'development']['Fee'].sum())
        test_fee_o = (test_fee.loc[test_fee['Department__c'] == 'operations']['Fee'].sum())
        test_fee_ss = (test_fee.loc[test_fee['Department__c'] == 'support']['Fee'].sum())

        self.assertEqual(total_fees, int(sum([test_fee_m, test_fee_s, test_fee_d, test_fee_o, test_fee_ss])))

    def test_avg(self):
        total_fees = generate_output('What is the avg Cat1 fees within Quality Assurance Category of the '
                                     'Development department?')
        self.assertEqual(total_fees, 319)

    def test_max(self):
        total_fees = generate_output('What is the max Cat1 fees within Quality Assurance Category of the '
                                     'Development department?')
        self.assertEqual(total_fees, 1197)

    def test_min(self):
        total_fees = generate_output('What is the min Cat1 fees within Quality Assurance Category of the '
                                     'Development department?')
        self.assertEqual(total_fees, 6)


if __name__ == '__main__':
    unittest.main()
