from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    browser.configure( slowmo=230, )
    """
    - Orders robots from RobotSpareBin Industries Inc.
    - Saves the order HTML receipt as a PDF file.
    - Saves the screenshot of the ordered robot.
    - Embeds the screenshot of the robot to the PDF receipt.
    - Creates ZIP archive of the receipts and the images.
    """
    open_robot_order_website()
    close_annoying_modal()
    orders = get_orders()
    i = 0
    for row in orders:
        fill_the_form_and_create_pdf(row)
        i += 1
        if i < (int(orders.size)) :
            order_new_robot()
    archive_receipts()
    print("Finished : order_robots_from_RobotSpareBin()")


def open_robot_order_website():
    """
    - Navigates to the given URL
    """
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    

def get_orders():
    """
    - Downloads the orders file, read it as a table, and return the result
    """
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True) 
    library = Tables()
    orders = library.read_table_from_csv(
        "orders.csv", columns=["Order number","Head","Body","Legs","Address"])
    print("### Found Table Colums / Rows : " + str(orders.columns) + " / " + str(orders.size))
    return orders
    

def fill_the_form_and_create_pdf(row):
    """
    - Fills in the order data and click the 'ORDER' button
    - Troubleshoots danger alerts
    - Embeds screenshots to recipes and creates final PDF
    """
    order_number = row['Order number']
    page = browser.page()
    page.select_option("#head", row['Head'])
    page.set_checked("#id-body-" + row['Body'], True)
    page.get_by_placeholder("Enter the part number for the legs").fill(row['Legs'])
    page.fill("#address", row['Address'])
    page.click("#order")

    alert_danger = page.locator("[class='alert alert-danger']").is_visible()
    if alert_danger :
        print ("Starting reordering max 10 times for Order Nr : " + order_number)
        i = 0
        while (alert_danger and i<10):
            i += 1
            page = browser.page()
            page.click("#order")
            alert_danger = page.locator("[class='alert alert-danger']").is_visible()
        if i==9 :
            print ("Reordering for Order Nr " + order_number + " NOT POSSIBLE!")
        else :
            alert_danger = False
            
    if not alert_danger :
        embed_screenshot_to_receipt(screenshot_robot(order_number), store_receipt_as_pdf(order_number))    


def store_receipt_as_pdf(order_number):
   """
   - Takes an argument (the order number - to be used in the file name to ensure a unique name) 
   - Returns a result (the file system path to the PDF file)
   """
   page = browser.page()
   receipt_path = f"output/receipts/receipt_f_order_{order_number}.pdf"
   PDF().html_to_pdf(page.locator("#receipt").inner_html(), receipt_path)
   return receipt_path


def screenshot_robot(order_number):
    """
    - Takes an argument (the order number - to be used in the file name to ensure a unique name) 
    - Returns a result (the file system path to the PNG file)
    """
    page = browser.page()
    png_path = f"output/screenshots/pic_f_order_{order_number}.png"
    page.locator("#robot-preview-image").screenshot(path=png_path)
    return png_path


def embed_screenshot_to_receipt(screenshot, pdf_file):
    """
    - Embeds the robot screenshot to the receipt PDF file
    """
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(image_path=screenshot, source_path=pdf_file, output_path=pdf_file)


def order_new_robot():
    """
    - Preps the page for new robot ordering
    """
    page = browser.page()
    page.click("#order-another")
    close_annoying_modal()


def archive_receipts():
    """
    - Archives all order receipts
    """
    ziparchive = Archive()
    ziparchive.archive_folder_with_zip("./output/receipts", "./output/receipts.zip")


def close_annoying_modal():
    """ 
    - Gets rid of that annoying modal that pops up when you open the robot order website
    """
    page = browser.page()
    page.click("button:text('Yep')")