import os
import re
import csv


class TextFileProcessor:
    def __init__(self):
        self.status = "Initialized"
        self.txt_list = []
        self.company_list = []
        self.company_data = []
        self.file_names = []
        self.data_folder = "LINKS_DATA"
        
    def get_txt_files(self):
        """Összegyűjti az aktuális könyvtár összes .txt fájlját"""
        self.status = "Searching for TXT files"
        print(f"Status: {self.status}")
        
        cwd = os.path.join(os.getcwd(),"LINKS_DATA")
        all_files = os.listdir(cwd)
        self.txt_list = [file for file in all_files if file.lower().endswith('.txt')]
        
        print(f"Found {len(self.txt_list)} TXT files")
        return self.txt_list
    
    def save_txt_list(self):
        """Elmenti a TXT fájlok listáját CSV-be"""
        self.status = "Saving TXT list to CSV"
        print(f"Status: {self.status}")
        
        with open('txt_list.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['TXT_Files'])
            for txt_file in self.txt_list:
                writer.writerow([txt_file])
        
        print("Saved txt_list.csv")
    
    def extract_company_info(self, content):
        """Kinyeri a company információkat regex-szel"""
        # COMPANY_LIST regex: <link rel="canonical" href és <meta name="og:site_name" content="CompanyWall Business" közti szöveg
        company_list_pattern = r'<link rel="canonical" href(.*?)<meta name="og:site_name" content="CompanyWall Business"'
        company_list_match = re.search(company_list_pattern, content, re.DOTALL)
        
        # COMPANY_DATA regex: <div>\s*<p> és </p>\s*</div> közti szöveg
        company_data_pattern = r'<div>\s*<p>(.*?)</p>\s*</div>'
        company_data_match = re.search(company_data_pattern, content, re.DOTALL)
        
        company_list = company_list_match.group(1).strip() if company_list_match else "NA"
        company_data = company_data_match.group(1).strip() if company_data_match else "NA"
        
        return company_list, company_data
    
    def process_txt_files(self):
        """Feldolgozza az összes TXT fájlt és kinyeri az információkat"""
        self.status = "Processing TXT files"
        print(f"Status: {self.status}")
        
        self.company_list.clear()
        self.company_data.clear()
        self.file_names.clear()
        cwd = os.path.join(os.getcwd(), "LINKS_DATA")
        for txt_file in self.txt_list:
            try:
                with open(os.path.join(cwd,txt_file), 'r', encoding='utf-8') as file:
                    content = file.read()
                
                company_list, company_data = self.extract_company_info(content)
                
                self.file_names.append(txt_file)
                self.company_list.append(company_list)
                self.company_data.append(company_data)
                
                print(f"Processed: {txt_file}")
                
            except Exception as e:
                print(f"Error processing {txt_file}: {str(e)}")
                # Hozzáadás "NA" értékekkel hiba esetén
                self.file_names.append(txt_file)
                self.company_list.append("NA")
                self.company_data.append("NA")
    
    def save_company_db(self):
        """Elmenti a company adatokat CSV-be"""
        self.status = "Saving company database"
        print(f"Status: {self.status}")
        
        with open('company_DB.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(['TXT_File_Name', 'COMPANY_LIST', 'COMPANY_DATA'])
            
            for i in range(len(self.file_names)):
                if self.company_list[i] != "NA" :
                    writer.writerow([
                        self.file_names[i],
                        self.company_list[i],
                        self.company_data[i]
                    ])
        
        print("Saved company_DB.csv")
        print(f"Processed {len(self.file_names)} files total")
    
    def run(self):
        """Futtatja a teljes folyamatot"""
        self.status = "Starting process"
        print(f"Status: {self.status}")
        
        # 1. TXT fájlok gyűjtése
        self.get_txt_files()
        
        if not self.txt_list:
            self.status = "No TXT files found"
            print(f"Status: {self.status}")
            return
        
        # 2. TXT lista mentése
        self.save_txt_list()
        
        # 3. TXT fájlok feldolgozása
        self.process_txt_files()
        
        # 4. Eredmények mentése
        self.save_company_db()
        
        self.status = "Process completed successfully"
        print(f"Status: {self.status}")


def main():
    """Fő függvény a program futtatásához"""
    processor = TextFileProcessor()
    processor.run()


if __name__ == "__main__":
    main()