from tinydb import TinyDB
import pandas as pd
from utils import create_pathdir, timestamp
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML


class Report:

    """

    The Report class is responsible for creating a report instance with access to a
    file JSON (database) managed by TinyDB library.

    :param ips: (list) A list with IPs of devices
    :param type: (str) Type of report. Options are: capacity, inventory

    """

    def __init__(self, ips=[list], type=str):

        """
        Create a new instance of Report
        """

        self.ips = ips
        self.type = type
        self.path = self.path_type_report(type)

    def path_type_report(self, type: str):

        """
        Returns the directory path of the type of report available.

        :param type: (str) Type of report. Options are: capacity, inventory
        """

        types = {
            "capacity": "/db/capacity_report",
            "inventory": "/db/inventory_report",
        }

        if type in types.keys():
            path = create_pathdir(types[type])
        return path

    def get_lastrecord(self, pathdb):

        """
        Read from a document JSON (database) the last record

        :param pathdb: (str)  Path to the JSON file (database)
        """

        db = TinyDB(pathdb)
        id = db.__len__()
        record = db.get(doc_id=id)

        return record

    def create_table(self):

        """
        Creates an HTML-format table filled with last records of every IP device
        from their JSON files
        """

        records = []
        for ip in self.ips:
            pathdb = self.path + ip + ".json"
            record = self.get_lastrecord(pathdb)
            records.append(record)

        df = pd.DataFrame(records)
        table_html = df.to_html()
        return table_html

    def render_pdfreport(self):

        """
        Reads an HTML report template and fills it with a table of records. Then it
        creates a PDF and HTML report
        """

        template_type = {
            "capacity": "report_capacity.html",
            "inventory": "report_inventory.html",
        }

        env = Environment(loader=FileSystemLoader("templates"))

        template = env.get_template(template_type[self.type])

        date = timestamp()
        filename = "report_{}_{}".format(self.type, date)
        pathdir = create_pathdir("/reports")

        template_vars = {
            # "Title" : "Report of {}".format(self.type),
            "Table": self.create_table(),
            "Date": date,
        }

        html_out = template.render(template_vars)

        # Creates the HTML file
        with open("{}/{}.html".format(pathdir, filename), "w") as f:
            f.write(html_out)

        # Creates the PDF file
        html = HTML(string=html_out, base_url="")
        html.write_pdf(
            "{}/{}.pdf".format(pathdir, filename),
            stylesheets=["templates/style.css"],
        )
