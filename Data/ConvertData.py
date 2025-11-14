import json
import pandas as pd

class ConverData():
    def excel_to_json(excel_path, json_path):
        # Đọc file excel vào dataframe
        df = pd.read_excel(excel_path)

        result = {"keywords": {}}

        for _, row in df.iterrows():
            params = {}

            # Tự động gom tất cả cột param_ thành dict
            for col in df.columns:
                if col.startswith("param_") and not pd.isna(row[col]):
                    params[col.replace("param_", "")] = row[col]

            # Thêm keyword vào JSON
            result["keywords"][row["keyword"]] = {
                "group": row["group"],
                "type": row["type"],
                "description": row["description"] if "description" in df.columns else "",
                "params": params
            }

        # Ghi JSON ra file
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4, ensure_ascii=False)

        print(f"Đã tạo JSON: {json_path}")



    def json_to_excel(json_path, excel_path):
        # Đọc JSON
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        rows = []

        for keyword, info in data["keywords"].items():
            base_row = {
                "keyword": keyword,
                "group": info.get("group", ""),
                "type": info.get("type", ""),
                "description": info.get("description", "")
            }

            # Tách params thành các cột param_xxx
            params = info.get("params", {})
            for p_name, p_value in params.items():
                base_row[f"param_{p_name}"] = p_value

            rows.append(base_row)

        # Tạo dataframe và ghi ra excel
        df = pd.DataFrame(rows)
        df.to_excel(excel_path, index=False)

        print(f"Đã tạo Excel: {excel_path}")

