from flask import Flask, render_template, request, redirect
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route("/")
def home():

    items_df = pd.read_csv("items.csv")

    usage_df = pd.read_csv("usage.csv")

    predictions = []


    for _, item_row in items_df.iterrows():

        item_name = item_row["item"]

        item_usage = usage_df[
            usage_df["item"] == item_name
        ]
        if len(item_usage) == 0:
            continue


        X = np.array(
            item_usage["day_num"]
        ).reshape(-1, 1)

        y = np.array(
            item_usage["daily_used"]
        )

        model = LinearRegression()

        model.fit(X, y)


        future_days = np.array([
            [len(X) + 1],
            [len(X) + 2],
            [len(X) + 3]
        ])

        future_predictions = model.predict(
            future_days
        )

        predicted_usage = round(
            max(
                0.1,
                future_predictions.mean()
            ),
            2
        )

        avg_usage = predicted_usage


        remaining = round(
            item_usage.iloc[-1]["remaining"],
            2
        )

        if avg_usage > 0:

            days_left = int(
                remaining / avg_usage
            )

        else:

            days_left = 0


        refill_date = (
            datetime.today() +
            timedelta(days=days_left)
        ).strftime("%d %b %Y")


        if days_left <= 2:

            status = "Critical"

            status_class = "critical"

        elif days_left <= 5:

            status = "Low"

            status_class = "low"

        else:

            status = "Good"

            status_class = "good"

        predictions.append({

            "item": item_name,

            "remaining": remaining,

            "avg_usage": avg_usage,

            "days_left": days_left,

            "refill_date": refill_date,

            "status": status,

            "status_class": status_class,

            "unit": item_row["unit"]
        })

    selected_item = "Milk"

    if request.args.get("item"):

        selected_item = request.args.get("item")

    graph_labels = []

    graph_values = []

    selected_usage = usage_df[
        usage_df["item"] == selected_item
    ]

    if len(selected_usage) > 0:

        graph_labels = selected_usage[
            "date"
        ].tolist()

        graph_values = selected_usage[
            "daily_used"
        ].tolist()

    return render_template(

        "index.html",

        items=items_df.to_dict(orient="records"),

        usage=usage_df.to_dict(orient="records"),

        predictions=predictions,

        graph_labels=graph_labels,

        graph_values=graph_values,

        selected_item=selected_item
    )

@app.route("/add_item", methods=["POST"])
def add_item():

    item_name = request.form["item_name"]

    quantity = request.form["quantity"]

    unit = request.form["unit"]

    avg_usage = request.form["avg_usage"]


    items_df = pd.read_csv("items.csv")

    new_item = pd.DataFrame([{

        "item": item_name,

        "unit": unit,

        "total": quantity,

        "avg": avg_usage,
    }])

    items_df = pd.concat(
        [items_df, new_item],
        ignore_index=True
    )

    items_df.to_csv(
        "items.csv",
        index=False
    )

    return redirect("/")

@app.route("/update_usage", methods=["POST"])
def update_usage():

    item = request.form["item"]

    used = float(request.form["used"])

    date = request.form["date"]

    usage_df = pd.read_csv("usage.csv")

    item_usage = usage_df[
        usage_df["item"] == item
    ]

    items_df = pd.read_csv("items.csv")

    item_row = items_df[
        items_df["item"] == item
    ].iloc[0]

    if len(item_usage) == 0:

        remaining = float(
            item_row["total"]
        )

        day_num = 1

    else:

        remaining = float(
            item_usage.iloc[-1]["remaining"]
        )

        day_num = int(
            item_usage.iloc[-1]["day_num"]
        ) + 1

    new_remaining = max(
        0,
        remaining - used
    )

    new_usage = pd.DataFrame([{

        "item": item,

        "date": date,

        "daily_used": used,

        "remaining": new_remaining,

        "day_num": day_num
    }])

    usage_df = pd.concat(
        [usage_df, new_usage],
        ignore_index=True
    )

    usage_df.to_csv(
        "usage.csv",
        index=False
    )

    return redirect("/")

@app.route("/delete_item", methods=["POST"])

def delete_item():

    item_name = request.form["item"]

    items_df = pd.read_csv("items.csv")

    items_df = items_df[
        items_df["item"] != item_name
    ]

    items_df.to_csv(
        "items.csv",
        index=False
    )

    usage_df = pd.read_csv("usage.csv")

    usage_df = usage_df[
        usage_df["item"] != item_name
    ]

    usage_df.to_csv(
        "usage.csv",
        index=False
    )

    return redirect("/")

if __name__ == "__main__":

    app.run(debug=True)