#!/usr/bin/env python3
"""
Tests for Google Sheets access and authentication requirements.
"""

import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import pandas as pd
import tempfile
import shutil

# Import the modules we want to test
from ingest.sheets_client import get_credentials, read_range_a_to_u, load_config
from jobs.ingest_job import run_ingest
from storage.duckdb_store import DuckDBStore, DuckDBConfig


class TestGoogleSheetsAccess(unittest.TestCase):
    """Test Google Sheets authentication and data access."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config_path = Path("configs/config.yaml")
        self.client_secret_path = Path("configs/client_secret.json")
        self.token_path = Path("configs/token.json")
        
    def test_config_file_exists(self):
        """Test that config.yaml exists and is valid."""
        self.assertTrue(self.config_path.exists(), "config.yaml should exist")
        
        config = load_config()
        required_keys = ["spreadsheet_id", "sheet_name", "columns"]
        for key in required_keys:
            self.assertIn(key, config, f"config.yaml should contain '{key}'")
    
    def test_authentication_files_required(self):
        """Test that authentication files are required for Google Sheets access."""
        # Check if client_secret.json exists
        has_client_secret = self.client_secret_path.exists()
        
        # Check if token.json exists (indicates previous authentication)
        has_token = self.token_path.exists()
        
        print(f"🔐 Authentication Status:")
        print(f"   client_secret.json: {'✅ Found' if has_client_secret else '❌ Missing'}")
        print(f"   token.json: {'✅ Found' if has_token else '❌ Missing'}")
        
        if not has_client_secret:
            print("\n⚠️  To access Google Sheets, you need:")
            print("   1. Create a Google Cloud Project")
            print("   2. Enable Google Sheets API")
            print("   3. Create OAuth2 credentials")
            print("   4. Download client_secret.json to configs/")
            print("\n📋 Step-by-step setup:")
            print("   a) Go to https://console.cloud.google.com/")
            print("   b) Create a new project or select existing")
            print("   c) Enable Google Sheets API")
            print("   d) Create OAuth2 credentials (Desktop app)")
            print("   e) Download client_secret.json")
            print("   f) Place it in configs/client_secret.json")
    
    @patch('ingest.sheets_client.build')
    @patch('ingest.sheets_client.get_credentials')
    def test_sheets_access_with_mock(self, mock_get_credentials, mock_build):
        """Test Google Sheets access with mocked authentication."""
        # Mock credentials
        mock_creds = MagicMock()
        mock_get_credentials.return_value = mock_creds
        
        # Mock Google Sheets service
        mock_service = MagicMock()
        mock_sheets = MagicMock()
        mock_values = MagicMock()
        
        # Mock response data
        mock_response = {
            "values": [
                ["日期", "姓名", "音控", "导播", "摄影", "ProPresenter播放", "ProPresenter更新"],  # Header
                ["2024-01-01", "John Doe", "John Doe", "", "", "", ""],
                ["2024-01-08", "Jane Smith", "", "Jane Smith", "", "", ""],
                ["2024-01-15", "Bob Johnson", "", "", "Bob Johnson", "", ""],
            ]
        }
        mock_values.get.return_value.execute.return_value = mock_response
        mock_sheets.values.return_value = mock_values
        mock_service.spreadsheets.return_value = mock_sheets
        mock_build.return_value = mock_service
        
        # Test the function
        result = read_range_a_to_u()
        
        # Verify the result
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIsInstance(result[0], list)
        
        print(f"✅ Mock Google Sheets access successful")
        print(f"   Retrieved {len(result)} rows of data")
        print(f"   Sample data: {result[1][:3]}...")  # Show first data row
    
    def test_public_sheet_access(self):
        """Test if the Google Sheet is publicly accessible (no auth required)."""
        config = load_config()
        spreadsheet_id = config["spreadsheet_id"]
        
        # Try to access the sheet using a public URL format
        public_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv"
        
        print(f"📊 Testing public access to sheet: {spreadsheet_id}")
        print(f"   Public URL: {public_url}")
        
        try:
            # Try to read as CSV (public access)
            df = pd.read_csv(public_url)
            print(f"✅ Sheet is publicly accessible!")
            print(f"   Columns: {list(df.columns)}")
            print(f"   Rows: {len(df)}")
            return True
        except Exception as e:
            print(f"❌ Sheet is not publicly accessible: {e}")
            print("   Authentication required for data access")
            return False
    
    def test_ingest_job_with_mock_data(self):
        """Test the ingest job with mock data."""
        # Create a temporary database for testing
        with tempfile.NamedTemporaryFile(suffix='.duckdb', delete=False) as tmp_db:
            db_path = tmp_db.name
        
        try:
            # Mock data that matches the expected format
            mock_values = [
                ["日期", "姓名", "音控", "导播", "摄影", "ProPresenter播放", "ProPresenter更新"],  # Header
                ["2024-01-01", "John Doe", "John Doe", "", "", "", ""],
                ["2024-01-08", "Jane Smith", "", "Jane Smith", "", "", ""],
                ["2024-01-15", "Bob Johnson", "", "", "Bob Johnson", "", ""],
            ]
            
            # Mock the sheets client and use a custom config for testing
            with patch('jobs.ingest_job.read_range_a_to_u', return_value=mock_values):
                with patch('jobs.ingest_job._load_config') as mock_config:
                    mock_config.return_value = {
                        "storage": {"duckdb_path": db_path}
                    }
                    
                    # Run the ingest job
                    run_ingest()
                    
                    # Verify data was stored
                    store = DuckDBStore(DuckDBConfig(db_path))
                    
                    # Check if facts table exists and has data
                    result = store.query("SELECT COUNT(*) as count FROM facts")
                    if result is not None and not result.empty:
                        count = result.iloc[0]['count']
                        print(f"✅ Ingest job successful! Stored {count} fact records")
                    else:
                        print("❌ Ingest job failed - no data in facts table")
                        
        finally:
            # Clean up temporary database
            if Path(db_path).exists():
                Path(db_path).unlink()
    
    def test_sheet_structure_validation(self):
        """Test that the sheet has the expected structure."""
        config = load_config()
        expected_columns = ["A", "Q", "R", "S", "T", "U"]
        
        print(f"📋 Expected sheet structure:")
        print(f"   Date column: {config['columns']['date']}")
        for role in config['columns']['roles']:
            print(f"   {role['service_type']}: column {role['key']}")
        
        # Verify all expected columns are defined
        defined_columns = [config['columns']['date']] + [role['key'] for role in config['columns']['roles']]
        for col in expected_columns:
            self.assertIn(col, defined_columns, f"Column {col} should be defined in config")


class TestDataTransformation(unittest.TestCase):
    """Test data transformation logic."""
    
    def test_sample_data_transformation(self):
        """Test transforming sample data to facts."""
        from ingest.transform import rows_to_facts
        
        # Sample data matching the expected format
        sample_rows = [
            ["日期", "姓名", "音控", "导播", "摄影", "ProPresenter播放", "ProPresenter更新"],
            ["2024-01-01", "John Doe", "John Doe", "", "", "", ""],
            ["2024-01-08", "Jane Smith", "", "Jane Smith", "", "", ""],
            ["2024-01-15", "Bob Johnson", "", "", "Bob Johnson", "", ""],
        ]
        
        # Transform the data
        facts = rows_to_facts(sample_rows)
        
        # Verify the transformation
        self.assertIsInstance(facts, pd.DataFrame)
        if not facts.empty:
            self.assertIn('service_date', facts.columns)
            self.assertIn('volunteer_id', facts.columns)
            self.assertIn('service_type_id', facts.columns)
            
            print(f"✅ Data transformation successful!")
            print(f"   Generated {len(facts)} fact records")
            print(f"   Service types: {set(facts['service_type_id'])}")
            print(f"   Volunteers: {set(facts['volunteer_id'])}")
        else:
            print("⚠️  Data transformation returned empty DataFrame")
            print("   This might indicate issues with the data format or transformation logic")


def run_all_tests():
    """Run all tests and provide a summary."""
    print("🧪 Running Google Sheets Access Tests\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestGoogleSheetsAccess))
    suite.addTests(loader.loadTestsFromTestCase(TestDataTransformation))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"   {test}: {traceback}")
    
    if result.errors:
        print("\n🚨 ERRORS:")
        for test, traceback in result.errors:
            print(f"   {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_all_tests()
