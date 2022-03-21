from tinydb import TinyDB
import pandas as pd
from utils import create_pathdir
from jinja2 import Environment, FileSystemLoader
import datetime
from weasyprint import HTML


class Report():

    def __init__(self, ips=[list], type=str):

        self.ips = ips
        self.type = type
        self.path = self.path_type_report(type)
    

    def path_type_report(self, type):

        types = {
            'capacity':'/db/capacity_report', 
            'inventory':'/db/inventory_report',
            }

        if type in types.keys():
            path = create_pathdir(types[type])
        return path


    def get_lastrecord(self,pathdb):
        
        db = TinyDB(pathdb)
        id = db.__len__()
        record = db.get(doc_id=id)

        return record

    def create_table(self):

        records = []
        for ip in self.ips:
            pathdb = self.path + ip + '.json'
            record = self.get_lastrecord(pathdb)
            records.append(record)
        
        df = pd.DataFrame(records)
        table_html = df.to_html()
        return table_html


    def render_pdfreport(self):

        template_type = {
            'capacity': 'report_capacity.html',
            'inventory': 'report_inventory.html'
        }

        env = Environment(loader=FileSystemLoader('templates'))
        
        template = env.get_template(template_type[self.type])

        date = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
        filename = "report_{}_{}".format(self.type,date)
        pathdir = create_pathdir('/reports')

        template_vars = {
                #"Title" : "Report of {}".format(self.type),
                 "Table": self.create_table(),
                 "Date": date
                 }

        html_out = template.render(template_vars)

        with open("{}/{}.html".format(pathdir,filename), 'w') as f:
            f.write(html_out)

        html = HTML(string=html_out, base_url="")

        html.write_pdf("{}/{}.pdf".format(pathdir,filename),stylesheets=["templates/style.css"])


        

