#!/usr/bin/env python3
"""Small native Mac GUI for ReliQuary vault operations."""

from __future__ import annotations

import os
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

from vaults.manager import VaultManager
from vaults.storage.local import LocalStorage
from vaults.storage.postgres import PostgresStorage
from vaults.storage.s3 import S3Storage


class ReliQuaryApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("ReliQuary Vault Console")
        self.geometry("1040x720")
        self.minsize(900, 620)
        self.manager: VaultManager | None = None
        self.current_vault_id = tk.StringVar()
        self.storage_mode = tk.StringVar(value="Local Mac folder")
        self.local_path = tk.StringVar(value=str(Path.home() / "ReliQuary Vaults"))
        self.database_url = tk.StringVar(value=os.environ.get("DATABASE_URL", ""))
        self.s3_bucket = tk.StringVar(value=os.environ.get("RELIQUARY_S3_BUCKET", ""))
        self.s3_region = tk.StringVar(value=os.environ.get("RELIQUARY_S3_REGION", "us-east-1"))
        self.s3_prefix = tk.StringVar(value=os.environ.get("RELIQUARY_S3_PREFIX", "reliquary"))
        self.s3_endpoint = tk.StringVar(value=os.environ.get("RELIQUARY_S3_ENDPOINT_URL", ""))
        self._build_ui()

    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=18)
        root.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(root)
        header.pack(fill=tk.X)
        ttk.Label(header, text="ReliQuary Vault Console", font=("Helvetica", 22, "bold")).pack(side=tk.LEFT)
        ttk.Button(header, text="Initialize Storage", command=self.initialize_storage).pack(side=tk.RIGHT)

        main = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True, pady=(18, 0))

        left = ttk.Frame(main, padding=10)
        right = ttk.Frame(main, padding=10)
        main.add(left, weight=1)
        main.add(right, weight=1)

        self._storage_panel(left)
        self._vault_panel(left)
        self._secret_panel(right)
        self._log_panel(right)

    def _storage_panel(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Storage target", padding=12)
        frame.pack(fill=tk.X)
        mode = ttk.Combobox(
            frame,
            textvariable=self.storage_mode,
            values=["Local Mac folder", "Postgres", "S3-compatible bucket"],
            state="readonly",
        )
        mode.pack(fill=tk.X)

        local_row = ttk.Frame(frame)
        local_row.pack(fill=tk.X, pady=(10, 0))
        ttk.Entry(local_row, textvariable=self.local_path).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(local_row, text="Choose Folder", command=self.choose_local_folder).pack(side=tk.LEFT, padx=(8, 0))

        ttk.Label(frame, text="DATABASE_URL").pack(anchor=tk.W, pady=(10, 0))
        ttk.Entry(frame, textvariable=self.database_url).pack(fill=tk.X)

        s3_grid = ttk.Frame(frame)
        s3_grid.pack(fill=tk.X, pady=(10, 0))
        ttk.Label(s3_grid, text="S3 bucket").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(s3_grid, text="Region").grid(row=0, column=1, sticky=tk.W, padx=(8, 0))
        ttk.Entry(s3_grid, textvariable=self.s3_bucket).grid(row=1, column=0, sticky=tk.EW)
        ttk.Entry(s3_grid, textvariable=self.s3_region).grid(row=1, column=1, sticky=tk.EW, padx=(8, 0))
        ttk.Label(s3_grid, text="Prefix").grid(row=2, column=0, sticky=tk.W, pady=(8, 0))
        ttk.Label(s3_grid, text="Endpoint URL, optional").grid(row=2, column=1, sticky=tk.W, padx=(8, 0), pady=(8, 0))
        ttk.Entry(s3_grid, textvariable=self.s3_prefix).grid(row=3, column=0, sticky=tk.EW)
        ttk.Entry(s3_grid, textvariable=self.s3_endpoint).grid(row=3, column=1, sticky=tk.EW, padx=(8, 0))
        s3_grid.columnconfigure(0, weight=1)
        s3_grid.columnconfigure(1, weight=1)

    def _vault_panel(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Vault", padding=12)
        frame.pack(fill=tk.X, pady=(14, 0))
        self.vault_name = tk.StringVar(value="research-vault")
        self.vault_owner = tk.StringVar(value="local-user")
        self.vault_description = tk.StringVar(value="Local encrypted ReliQuary vault")
        for label, variable in (
            ("Name", self.vault_name),
            ("Owner", self.vault_owner),
            ("Description", self.vault_description),
            ("Current vault ID", self.current_vault_id),
        ):
            ttk.Label(frame, text=label).pack(anchor=tk.W)
            ttk.Entry(frame, textvariable=variable).pack(fill=tk.X, pady=(0, 8))
        ttk.Button(frame, text="Create Vault", command=self.create_vault).pack(fill=tk.X)
        ttk.Button(frame, text="List Vaults", command=self.list_vaults).pack(fill=tk.X, pady=(8, 0))

    def _secret_panel(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Secret", padding=12)
        frame.pack(fill=tk.X)
        self.secret_name = tk.StringVar(value="database-password")
        ttk.Label(frame, text="Secret name").pack(anchor=tk.W)
        ttk.Entry(frame, textvariable=self.secret_name).pack(fill=tk.X, pady=(0, 8))
        ttk.Label(frame, text="Secret value").pack(anchor=tk.W)
        self.secret_value = tk.Text(frame, height=5, wrap=tk.WORD)
        self.secret_value.insert("1.0", "replace-with-a-real-secret")
        self.secret_value.pack(fill=tk.X, pady=(0, 8))
        actions = ttk.Frame(frame)
        actions.pack(fill=tk.X)
        ttk.Button(actions, text="Store Secret", command=self.store_secret).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(actions, text="Retrieve Secret", command=self.retrieve_secret).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))

    def _log_panel(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Result log", padding=12)
        frame.pack(fill=tk.BOTH, expand=True, pady=(14, 0))
        self.log_text = tk.Text(frame, height=16, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log("Pick a storage target, initialize it, then create a vault and store a secret.")

    def choose_local_folder(self) -> None:
        selected = filedialog.askdirectory(initialdir=self.local_path.get() or str(Path.home()))
        if selected:
            self.local_path.set(selected)

    def log(self, message: str) -> None:
        self.log_text.insert(tk.END, message.rstrip() + "\n")
        self.log_text.see(tk.END)

    def run_task(self, fn) -> None:
        def wrapped() -> None:
            try:
                fn()
            except Exception as exc:
                self.after(0, lambda: messagebox.showerror("ReliQuary error", str(exc)))
                self.after(0, lambda: self.log(f"ERROR: {exc}"))

        threading.Thread(target=wrapped, daemon=True).start()

    def initialize_storage(self) -> None:
        def task() -> None:
            mode = self.storage_mode.get()
            if mode == "Local Mac folder":
                storage = LocalStorage(self.local_path.get())
            elif mode == "Postgres":
                storage = PostgresStorage(self.database_url.get())
            else:
                if not self.s3_bucket.get():
                    raise ValueError("S3 bucket is required.")
                storage = S3Storage(
                    bucket_name=self.s3_bucket.get(),
                    region_name=self.s3_region.get(),
                    prefix=self.s3_prefix.get(),
                    endpoint_url=self.s3_endpoint.get() or None,
                )
            self.manager = VaultManager(storage)
            self.after(0, lambda: self.log(f"Initialized {mode} storage."))

        self.run_task(task)

    def require_manager(self) -> VaultManager:
        if self.manager is None:
            raise RuntimeError("Initialize storage first.")
        return self.manager

    def create_vault(self) -> None:
        def task() -> None:
            vault = self.require_manager().create_vault(
                name=self.vault_name.get(),
                description=self.vault_description.get(),
                owner_id=self.vault_owner.get(),
            )
            self.after(0, lambda: self.current_vault_id.set(vault.vault_id))
            self.after(0, lambda: self.log(f"Created vault {vault.vault_id} for {vault.owner_id}."))

        self.run_task(task)

    def list_vaults(self) -> None:
        def task() -> None:
            vaults = self.require_manager().list_vaults()
            lines = [f"{vault.vault_id} | {vault.owner_id} | {vault.name}" for vault in vaults]
            self.after(0, lambda: self.log("Vaults:\n" + ("\n".join(lines) if lines else "No vaults found.")))

        self.run_task(task)

    def store_secret(self) -> None:
        def task() -> None:
            secret = self.require_manager().store_secret(
                self.current_vault_id.get().strip(),
                self.secret_name.get().strip(),
                self.secret_value.get("1.0", tk.END).strip(),
            )
            self.after(0, lambda: self.log(f"Stored secret {secret.secret_name} as record {secret.secret_id}."))

        self.run_task(task)

    def retrieve_secret(self) -> None:
        def task() -> None:
            secret = self.require_manager().retrieve_secret(
                self.current_vault_id.get().strip(),
                self.secret_name.get().strip(),
            )
            self.after(0, lambda: self.log(f"Retrieved {secret.secret_name}: {secret.secret_value}"))

        self.run_task(task)


if __name__ == "__main__":
    ReliQuaryApp().mainloop()
