import unittest
from jsonsql import JsonSQL


class TestLogicParse(unittest.TestCase):

    def test_invalid_input(self):
        jsonsql = JsonSQL([], [], [], [], {})
        input = {'invalid': 'value'}
        result, msg = jsonsql.logic_parse(input)
        self.assertFalse(result)
        self.assertEqual(msg, "Invalid Input - invalid")

    def test_bad_and_non_list(self):
        jsonsql = JsonSQL([], [], [], [], {})
        input = {'AND': 'value'}
        result, msg = jsonsql.logic_parse(input)
        self.assertFalse(result)
        self.assertEqual(msg, "Bad AND, non list")

    def test_bad_column_type(self):
        jsonsql = JsonSQL([], [], [], [], {'col1': str})
        input = {'col1': 123}
        result, msg = jsonsql.logic_parse(input)
        self.assertFalse(result)
        self.assertEqual(msg, "Bad col1, non <class 'str'>")

    def test_valid_single_column(self):
        jsonsql = JsonSQL([], [], [], [], {'col1': str})
        input = {'col1': 'value'}
        result, sql, params = jsonsql.logic_parse(input)
        self.assertTrue(result)
        self.assertEqual(sql, "col1 = ?")
        self.assertEqual(params, 'value')

    def test_invalid_boolean_len(self):
        jsonsql = JsonSQL([], [], [], [], {})
        input = {'AND': ['cond']}
        result, msg = jsonsql.logic_parse(input)
        self.assertFalse(result)
        self.assertEqual(msg, "Invalid boolean length, must be >= 2")

    def test_valid_multi_condition(self):
        jsonsql = JsonSQL([], [], [], [], {'col1': str, 'col2': str})
        input = {'AND': [{'col1': 'value1'}, {'col2': 'value2'}]}
        result, sql, params = jsonsql.logic_parse(input)
        self.assertTrue(result)
        self.assertEqual(sql, "(col1 = ? AND col2 = ?)")
        self.assertEqual(params, ('value1', 'value2'))


class TestSQLParse(unittest.TestCase):

    def test_missing_argument(self):
        jsonsql = JsonSQL(['SELECT'], ['*'], ['table1'], ['WHERE'], {})
        input = {'query': 'SELECT', 'items': ['*'], "connection": "WHERE"}
        result, msg = jsonsql.sql_parse(input)
        self.assertFalse(result)
        self.assertEqual(msg, "Missing argument table")

    def test_bad_query(self):
        jsonsql = JsonSQL(['SELECT'], ['*'], ['table1'], ['WHERE'], {})
        input = {'query': 'INSERT', 'items': [
            '*'], 'table': 'table1', 'connection': 'WHERE'}
        result, msg = jsonsql.sql_parse(input)
        self.assertFalse(result)
        self.assertEqual(msg, "Query not allowed - INSERT")

    def test_bad_item(self):
        jsonsql = JsonSQL(['SELECT'], ['good'], ['table1'], ['WHERE'], {})
        input = {'query': 'SELECT', 'items': [
            'bad'], 'table': 'table1', 'connection': 'WHERE'}
        result, msg = jsonsql.sql_parse(input)
        self.assertFalse(result)
        self.assertEqual(msg, "Item not allowed - ['bad']")

    def test_bad_table(self):
        jsonsql = JsonSQL(['SELECT'], ['*'], ['table1'], ['WHERE'], {})
        input = {'query': 'SELECT', 'items': [
            '*'], 'table': 'bad', 'connection': 'WHERE'}
        result, msg = jsonsql.sql_parse(input)
        self.assertFalse(result)
        self.assertEqual(msg, "Table not allowed - bad")


if __name__ == "__main__":
    unittest.main()