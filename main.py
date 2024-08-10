import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("Choose which tool you need:")
ListOfTools = [
    [0, 'CASE'], [1, 'Email'], [2, 'PDF'], [3, 'ISO'], [4, 'OVA'], [5, 'URL'],
    [6, 'JSON'], [7, 'DB'], [8, 'PNG'], [9, 'CODE'], [10, 'EXE / DMG'], [11, 'EVENT VIEWER']
]

for tool in ListOfTools:
    print(f"{tool[0]}: {tool[1]}")

while True:
    Choice = input("Choose the tool you need or type 'exit' to quit: ")
    
    if Choice == 'exit':
        print("Bye!")
        break
    elif Choice == "0":
        print("CASE was selected")
        import Tools.CASE as CASE
        CASE.main()
        break
    elif Choice == "1":
        print("Email Analysis was selected")
        import Tools.Email_Analysis as Email_Analysis
        Email_Analysis.main()
        break
    elif Choice == "2":
        print("PDF Analysis was selected")
        import Tools.PDF_Analysis as PDF_Analysis
        PDF_Analysis.main()
        break
    elif Choice == "3":
        print("ISO Analysis was selected")
        import Tools.ISO_Analysis as ISO_Analysis
        ISO_Analysis.main()
        break
    elif Choice == "4":
        print("OVA Analysis was selected")
        import Tools.OVA_Analysis as OVA_Analysis
        OVA_Analysis.main()
        break
    elif Choice == "5":
        print("URL Analysis was selected")
        import Tools.URL_Analysis as URL_Analysis
        URL_Analysis.main()
        break
    elif Choice == "6":
        print("JSON Analysis was selected")
        import Tools.JSON_Analysis as JSON_Analysis
        JSON_Analysis.main()
        break
    elif Choice == "7":
        print("DB was selected")
        import DB.main_DB as main_DB
        main_DB.main()
        break
    elif Choice == "8":
        print("PNG Analysis was selected")
        import Tools.PNG_Analysis as PNG_Analysis
        PNG_Analysis.main()
        break
    elif Choice == "9":
        print("CODE Analysis was selected")
        import Tools.CODE_Analysis as CODE_Analysis
        CODE_Analysis.main()
        break
    elif Choice == "10":
        print("EXE / DMG Analysis was selected")
        import Tools.EXE_DMG_Analysis as EXE_DMG_Analysis
        EXE_DMG_Analysis.main()
        break
    elif Choice == "11":
        print("EVENT VIEWER was selected")
        import Tools.Event_Viewer as Event_Viewer
        Event_Viewer.main()
        break
    else:
        print("Invalid choice. Please select a valid tool.")
