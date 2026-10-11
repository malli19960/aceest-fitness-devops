import json
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app import create_app
from werkzeug.serving import make_server


class FitnessGuiDemo:
    def __init__(self, root, api_server):
        self.root = root
        self.api_server = api_server
        self.api_url = f"http://127.0.0.1:{api_server.server_port}"
        self.root.title("ACEest Fitness & Gym - API Feature Demo")
        self.root.geometry("1100x760")
        self.root.minsize(900, 620)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        self.client_fields = {}
        self.client_id_var = tk.StringVar()
        self.plan_goal_var = tk.StringVar(value="fat loss")
        self.plan_age_var = tk.StringVar(value="28")
        self.plan_height_var = tk.StringVar(value="175")
        self.plan_weight_var = tk.StringVar(value="70")

        heading = ttk.Label(
            root,
            text="ACEest Fitness & Gym — Flask API Feature Demo",
            font=("Segoe UI", 18, "bold"),
        )
        heading.pack(padx=12, pady=(12, 4))
        ttk.Label(
            root,
            text="This desktop interface uses the existing Flask API and its SQLite database.",
        ).pack(pady=(0, 8))

        self.tabs = ttk.Notebook(root)
        self.tabs.pack(fill="both", expand=True, padx=12, pady=8)
        self._build_plans_tab()
        self._build_clients_tab()
        self._build_activity_tab()

    def api_request(self, method, path, payload=None):
        body = None
        headers = {}
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = Request(
            f"{self.api_url}{path}",
            data=body,
            headers=headers,
            method=method,
        )
        try:
            with urlopen(request, timeout=5) as response:
                if response.status == 204:
                    return None
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            try:
                detail = json.loads(error.read().decode("utf-8")).get(
                    "error", error.reason
                )
            except (json.JSONDecodeError, UnicodeDecodeError):
                detail = error.reason
            raise ValueError(f"API returned {error.code}: {detail}") from error
        except URLError as error:
            raise RuntimeError(f"Could not reach the local Flask API: {error.reason}") from error

    def show_result(self, widget, value):
        widget.configure(state="normal")
        widget.delete("1.0", tk.END)
        widget.insert("1.0", json.dumps(value, indent=2, ensure_ascii=False))
        widget.configure(state="disabled")

    def show_error(self, error):
        messagebox.showerror("Request failed", str(error), parent=self.root)

    def make_result_box(self, parent):
        box = tk.Text(parent, wrap="word", height=18, state="disabled")
        box.pack(fill="both", expand=True, padx=8, pady=8)
        return box

    def _build_plans_tab(self):
        tab = ttk.Frame(self.tabs, padding=10)
        self.tabs.add(tab, text="Programs & Plan")

        fields = [
            ("Goal", self.plan_goal_var, ("fat loss", "muscle gain", "beginner", "performance")),
            ("Age", self.plan_age_var, None),
            ("Height (cm)", self.plan_height_var, None),
            ("Weight (kg)", self.plan_weight_var, None),
        ]
        controls = ttk.Frame(tab)
        controls.pack(fill="x")
        for column, (label, variable, options) in enumerate(fields):
            ttk.Label(controls, text=label).grid(row=0, column=column, sticky="w", padx=5)
            if options:
                ttk.Combobox(
                    controls,
                    textvariable=variable,
                    values=options,
                    state="readonly",
                    width=18,
                ).grid(row=1, column=column, sticky="ew", padx=5, pady=4)
            else:
                ttk.Entry(controls, textvariable=variable, width=14).grid(
                    row=1, column=column, sticky="ew", padx=5, pady=4
                )
            controls.columnconfigure(column, weight=1)

        buttons = ttk.Frame(tab)
        buttons.pack(fill="x", pady=5)
        ttk.Button(buttons, text="Get personalized plan", command=self.load_plan).pack(
            side="left", padx=5
        )
        ttk.Button(buttons, text="List all programs", command=self.load_programs).pack(
            side="left", padx=5
        )
        ttk.Button(buttons, text="Get summary", command=self.load_summary).pack(
            side="left", padx=5
        )
        self.plan_result = self.make_result_box(tab)

    def plan_query(self):
        return urlencode(
            {
                "goal": self.plan_goal_var.get(),
                "age": self.plan_age_var.get(),
                "height": self.plan_height_var.get(),
                "weight": self.plan_weight_var.get(),
            }
        )

    def load_plan(self):
        try:
            result = self.api_request("GET", f"/api/plan?{self.plan_query()}")
            self.show_result(self.plan_result, result)
        except (ValueError, RuntimeError) as error:
            self.show_error(error)

    def load_programs(self):
        try:
            self.show_result(self.plan_result, self.api_request("GET", "/api/programs"))
        except (ValueError, RuntimeError) as error:
            self.show_error(error)

    def load_summary(self):
        try:
            result = self.api_request("GET", f"/api/summary?{self.plan_query()}")
            self.show_result(self.plan_result, result)
        except (ValueError, RuntimeError) as error:
            self.show_error(error)

    def _build_clients_tab(self):
        tab = ttk.Frame(self.tabs, padding=10)
        self.tabs.add(tab, text="Client Profiles")
        form = ttk.LabelFrame(tab, text="Client details", padding=8)
        form.pack(fill="x")

        definitions = [
            ("Name", "name", ""),
            ("Age", "age", ""),
            ("Height (cm)", "height_cm", ""),
            ("Weight (kg)", "weight_kg", ""),
            ("Goal", "goal", ""),
            ("Experience", "experience", "beginner"),
        ]
        for index, (label, key, default) in enumerate(definitions):
            row, column = divmod(index, 3)
            ttk.Label(form, text=label).grid(row=row * 2, column=column, sticky="w", padx=5)
            variable = tk.StringVar(value=default)
            ttk.Entry(form, textvariable=variable).grid(
                row=row * 2 + 1, column=column, sticky="ew", padx=5, pady=(0, 6)
            )
            self.client_fields[key] = variable
            form.columnconfigure(column, weight=1)

        actions = ttk.Frame(tab)
        actions.pack(fill="x", pady=6)
        ttk.Button(actions, text="Create client", command=self.create_client).pack(
            side="left", padx=3
        )
        ttk.Button(actions, text="Update selected", command=self.update_client).pack(
            side="left", padx=3
        )
        ttk.Button(actions, text="Delete selected", command=self.delete_client).pack(
            side="left", padx=3
        )
        ttk.Button(actions, text="Refresh clients", command=self.refresh_clients).pack(
            side="left", padx=3
        )
        ttk.Label(actions, text="Selected client ID:").pack(side="left", padx=(14, 3))
        ttk.Entry(actions, textvariable=self.client_id_var, width=8, state="readonly").pack(
            side="left"
        )

        self.client_table = ttk.Treeview(
            tab,
            columns=("id", "name", "age", "weight", "goal", "bmi"),
            show="headings",
            height=8,
        )
        for key, label, width in [
            ("id", "ID", 50),
            ("name", "Name", 180),
            ("age", "Age", 70),
            ("weight", "Weight (kg)", 100),
            ("goal", "Goal", 150),
            ("bmi", "BMI", 80),
        ]:
            self.client_table.heading(key, text=label)
            self.client_table.column(key, width=width)
        self.client_table.pack(fill="both", expand=True, padx=2, pady=5)
        self.client_table.bind("<<TreeviewSelect>>", self.select_client)
        self.client_result = self.make_result_box(tab)
        self.refresh_clients()

    def client_payload(self):
        try:
            return {
                "name": self.client_fields["name"].get().strip(),
                "age": int(self.client_fields["age"].get()),
                "height_cm": float(self.client_fields["height_cm"].get()),
                "weight_kg": float(self.client_fields["weight_kg"].get()),
                "goal": self.client_fields["goal"].get().strip(),
                "experience": self.client_fields["experience"].get().strip(),
            }
        except ValueError as error:
            raise ValueError("Age, height, and weight must be valid numbers.") from error

    def create_client(self):
        try:
            result = self.api_request("POST", "/api/clients", self.client_payload())
            self.show_result(self.client_result, result)
            self.refresh_clients()
        except (ValueError, RuntimeError) as error:
            self.show_error(error)

    def update_client(self):
        try:
            client_id = self.client_id_var.get()
            if not client_id:
                raise ValueError("Select a client before updating.")
            result = self.api_request(
                "PUT", f"/api/clients/{client_id}", self.client_payload()
            )
            self.show_result(self.client_result, result)
            self.refresh_clients()
        except (ValueError, RuntimeError) as error:
            self.show_error(error)

    def delete_client(self):
        client_id = self.client_id_var.get()
        if not client_id:
            self.show_error(ValueError("Select a client before deleting."))
            return
        if not messagebox.askyesno(
            "Delete client",
            "Delete this client and their workout/progress records?",
            parent=self.root,
        ):
            return
        try:
            self.api_request("DELETE", f"/api/clients/{client_id}")
            self.client_id_var.set("")
            self.show_result(self.client_result, {"deleted_client_id": int(client_id)})
            self.refresh_clients()
        except (ValueError, RuntimeError) as error:
            self.show_error(error)

    def refresh_clients(self):
        try:
            result = self.api_request("GET", "/api/clients")
            for item in self.client_table.get_children():
                self.client_table.delete(item)
            for client in result["clients"]:
                self.client_table.insert(
                    "",
                    tk.END,
                    values=(
                        client["id"],
                        client["name"],
                        client["age"],
                        client["weight_kg"],
                        client["goal"],
                        client["bmi"],
                    ),
                )
            self.show_result(self.client_result, result)
        except (ValueError, RuntimeError) as error:
            self.show_error(error)

    def select_client(self, _event=None):
        selected = self.client_table.selection()
        if not selected:
            return
        values = self.client_table.item(selected[0], "values")
        client_id = values[0]
        self.client_id_var.set(client_id)
        try:
            client = self.api_request("GET", f"/api/clients/{client_id}")["client"]
            for key in ("name", "age", "height_cm", "weight_kg", "goal", "experience"):
                self.client_fields[key].set(str(client[key]))
            self.show_result(self.client_result, {"client": client})
        except (ValueError, RuntimeError) as error:
            self.show_error(error)

    def _build_activity_tab(self):
        tab = ttk.Frame(self.tabs, padding=10)
        self.tabs.add(tab, text="Workouts & Progress")
        selection = ttk.Frame(tab)
        selection.pack(fill="x", pady=(0, 8))
        ttk.Label(selection, text="Client ID (select a client on Client Profiles):").pack(
            side="left"
        )
        ttk.Entry(selection, textvariable=self.client_id_var, width=10, state="readonly").pack(
            side="left", padx=6
        )

        columns = ttk.Frame(tab)
        columns.pack(fill="both", expand=True)
        workout_box = ttk.LabelFrame(columns, text="Log a workout", padding=8)
        workout_box.pack(side="left", fill="both", expand=True, padx=(0, 5))
        self.workout_type_var = tk.StringVar(value="Strength training")
        self.duration_var = tk.StringVar(value="45")
        self.workout_date_var = tk.StringVar()
        self.workout_notes_var = tk.StringVar()
        for row, (label, variable) in enumerate(
            [
                ("Workout type", self.workout_type_var),
                ("Duration (minutes)", self.duration_var),
                ("Date (YYYY-MM-DD; optional)", self.workout_date_var),
                ("Notes (optional)", self.workout_notes_var),
            ]
        ):
            ttk.Label(workout_box, text=label).grid(row=row * 2, column=0, sticky="w", pady=3)
            ttk.Entry(workout_box, textvariable=variable).grid(
                row=row * 2 + 1, column=0, sticky="ew", pady=(0, 5)
            )
        ttk.Button(workout_box, text="Save workout", command=self.save_workout).grid(
            row=8, column=0, sticky="ew", pady=5
        )
        ttk.Button(
            workout_box, text="Load workout history", command=self.load_workouts
        ).grid(row=9, column=0, sticky="ew", pady=5)
        workout_box.columnconfigure(0, weight=1)

        progress_box = ttk.LabelFrame(columns, text="Record progress", padding=8)
        progress_box.pack(side="left", fill="both", expand=True, padx=(5, 0))
        self.progress_weight_var = tk.StringVar()
        self.adherence_var = tk.StringVar(value="80")
        self.progress_notes_var = tk.StringVar()
        for row, (label, variable) in enumerate(
            [
                ("Weight (kg)", self.progress_weight_var),
                ("Weekly adherence (0-100%)", self.adherence_var),
                ("Notes (optional)", self.progress_notes_var),
            ]
        ):
            ttk.Label(progress_box, text=label).grid(row=row * 2, column=0, sticky="w", pady=3)
            ttk.Entry(progress_box, textvariable=variable).grid(
                row=row * 2 + 1, column=0, sticky="ew", pady=(0, 5)
            )
        ttk.Button(progress_box, text="Save progress", command=self.save_progress).grid(
            row=6, column=0, sticky="ew", pady=5
        )
        ttk.Button(
            progress_box, text="Load progress history", command=self.load_progress
        ).grid(row=7, column=0, sticky="ew", pady=5)
        progress_box.columnconfigure(0, weight=1)

        self.activity_result = self.make_result_box(tab)

    def selected_client_id(self):
        client_id = self.client_id_var.get()
        if not client_id:
            raise ValueError("Select a client on the Client Profiles tab first.")
        return client_id

    def save_workout(self):
        try:
            payload = {
                "workout_type": self.workout_type_var.get().strip(),
                "duration_min": int(self.duration_var.get()),
                "notes": self.workout_notes_var.get(),
            }
            if self.workout_date_var.get().strip():
                payload["workout_date"] = self.workout_date_var.get().strip()
            result = self.api_request(
                "POST",
                f"/api/clients/{self.selected_client_id()}/workouts",
                payload,
            )
            self.show_result(self.activity_result, result)
        except (ValueError, RuntimeError) as error:
            self.show_error(error)

    def load_workouts(self):
        try:
            result = self.api_request(
                "GET", f"/api/clients/{self.selected_client_id()}/workouts"
            )
            self.show_result(self.activity_result, result)
        except (ValueError, RuntimeError) as error:
            self.show_error(error)

    def save_progress(self):
        try:
            payload = {
                "weight_kg": float(self.progress_weight_var.get()),
                "adherence_pct": int(self.adherence_var.get()),
                "notes": self.progress_notes_var.get(),
            }
            result = self.api_request(
                "POST",
                f"/api/clients/{self.selected_client_id()}/progress",
                payload,
            )
            self.show_result(self.activity_result, result)
        except (ValueError, RuntimeError) as error:
            self.show_error(error)

    def load_progress(self):
        try:
            result = self.api_request(
                "GET", f"/api/clients/{self.selected_client_id()}/progress"
            )
            self.show_result(self.activity_result, result)
        except (ValueError, RuntimeError) as error:
            self.show_error(error)

    def close(self):
        self.api_server.shutdown()
        self.api_server.server_close()
        self.root.destroy()


def main():
    api_server = make_server("127.0.0.1", 0, create_app(), threaded=True)
    threading.Thread(target=api_server.serve_forever, daemon=True).start()
    root = tk.Tk()
    FitnessGuiDemo(root, api_server)
    root.mainloop()


if __name__ == "__main__":
    main()
