from flask import Flask, render_template, request, redirect, url_for
import os
import json
from datetime import datetime
import pprint

app = Flask(__name__)


@app.route("/")
def home():
    menu_data = []
    if os.path.isfile("menu_item_file.json"):
        with open("menu_item_file.json", "r") as menu_items_list:
            menu_data = json.load(menu_items_list)
    return render_template("index.html", menu_list=menu_data)


@app.route("/edit_menu/", methods=["GET", "POST"])
def edit_menu():
    if request.method == "GET":
        return render_template("edit_menu.html", message="")
    elif request.method == "POST":
        item_name = request.form["menuItem"]
        price_or_pass = request.form["priceOrDelete"].lower()
        message = ""

        menu_data = []
        if os.path.isfile("menu_item_file.json"):
            with open("menu_item_file.json", "r") as menu_items_list:
                menu_data = json.load(menu_items_list)
            if price_or_pass.lower() == "delete":
                is_available_in_menu = False
                for index, item in enumerate(menu_data):
                    if item["item_name"].lower() == item_name.lower():
                        is_available_in_menu = True
                        del menu_data[index]
                        break
                if is_available_in_menu:
                    message = item_name + " has been deleted from menu!"
                else:
                    message = item_name + " does not exist in menu!"
            elif price_or_pass.isdigit():
                is_available_in_menu = False
                message = item_name + " has been updated in the menu!"
                for index, item in enumerate(menu_data):
                    if item["item_name"] == item_name:
                        menu_data[index] = {"item_name": item_name, "price": int(price_or_pass)}
                        is_available_in_menu = True
                        break
                if not is_available_in_menu:
                    message = item_name + " has been added in the menu!"
                    menu_data.append({"item_name": item_name, "price": int(price_or_pass)})
        else:
            menu_data.append({"item_name": item_name, "price": int(price_or_pass)})
            message = item_name + " has been added in the menu!"
        with open("menu_item_file.json", "w") as menu_items_list:
            json.dump(menu_data, menu_items_list)

        return render_template("edit_menu.html", message=message)


@app.route("/order/", methods=["POST"])
def order():
    order_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    sales_data = []
    if os.path.isfile("sales.json"):
        with open("sales.json", "r") as sales_file:
            sales_data = json.load(sales_file)
    current_order = request.get_json()
    current_order["order_time"] = order_time
    sales_data.append(json.dumps(current_order))
    with open("sales.json", "w") as sales_file:
        json.dump(sales_data, sales_file)
    return redirect(url_for("home"))


@app.route("/sales/", methods=["GET", "POST"])
def sales():
    sales_data = []
    sales_count = {}
    start_date = datetime.now()
    end_date = datetime.now()
    if os.path.isfile("sales.json"):
        with open("sales.json", "r") as sales_file:
            sales_data = json.load(sales_file)

    today = datetime.today()
    start_date = datetime(today.year, today.month, 1)
    if request.method == "POST":
        if request.form["from-date"] != '':
            start_date = datetime(int(request.form["from-date"].split("-")[0]),
                                  int(request.form["from-date"].split("-")[1]),
                                  int(request.form["from-date"].split("-")[2]))
        if request.form["to-date"] != '':
            end_date = datetime(int(request.form["to-date"].split("-")[0]),
                                int(request.form["to-date"].split("-")[1]),
                                int(request.form["to-date"].split("-")[2]))
        pprint.pprint(request.form["from-date"])
    for each_sale in sales_data:
        sale = json.loads(each_sale)
        if start_date <= datetime.strptime(sale["order_time"], '%m/%d/%Y, %H:%M:%S') < end_date:
            for item in sale.keys():
                if item != "order_time":
                    if item in sales_count.keys():
                        sales_count.update({str(item): sales_count[item]+int(sale[item])})
                    else:
                        sales_count[str(item)] = int(sale[item])

    return render_template("sales.html", sales_list=sales_count,
                           from_date=datetime.strftime(start_date, '%d/%m/%Y, %H:%M:%S'),
                           to_date=datetime.strftime(end_date, '%d/%m/%Y, %H:%M:%S'))


@app.route("/sales/")
def sales_by_year():
    sales_data = []
    sales_count = {}
    if os.path.isfile("sales.json"):
        with open("sales.json", "r") as sales_file:
            sales_data = json.load(sales_file)

    today = datetime.today()
    first_day_of_month = datetime(today.year, today.month, 1)
    for each_sale in sales_data:
        sale = json.loads(each_sale)
        if datetime.strptime(sale["order_time"], '%m/%d/%Y, %H:%M:%S') >= first_day_of_month:
            for item in sale.keys():
                if item != "order_time":
                    if item in sales_count.keys():
                        sales_count.update({str(item): sales_count[item]+int(sale[item])})
                    else:
                        sales_count[str(item)] = int(sale[item])

    return render_template("sales.html", sales_list=sales_count)


@app.route("/search/")
def search():
    query = request.args.get("q")
    filtered_menu_data = []
    if query:
        if os.path.isfile("menu_item_file.json"):
            with open("menu_item_file.json", "r") as menu_items_list:
                menu_data = json.load(menu_items_list)
        for item in menu_data:
            if query.lower() in item["item_name"].lower():
                filtered_menu_data.append(item)
    else:
        filtered_menu_data = []

    return render_template("search.html", filtered_list=filtered_menu_data)
