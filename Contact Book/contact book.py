import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import os

class ContactBook:
    def __init__(self, root):
        self.root = root
        self.root.title("Contact Book")
        
        self.contacts = self.load_contacts()
        
        self.name_label = tk.Label(root, text="Name")
        self.name_label.grid(row=0, column=0)
        self.name_entry = tk.Entry(root)
        self.name_entry.grid(row=0, column=1)
        
        self.phone_label = tk.Label(root, text="Phone")
        self.phone_label.grid(row=1, column=0)
        self.phone_entry = tk.Entry(root)
        self.phone_entry.grid(row=1, column=1)
        
        self.add_button = tk.Button(root, text="Add Contact", command=self.add_contact)
        self.add_button.grid(row=2, column=0, columnspan=2)
        
        self.update_button = tk.Button(root, text="Update Selected", command=self.update_contact)
        self.update_button.grid(row=3, column=0, columnspan=2)
        
        self.remove_button = tk.Button(root, text="Remove Selected", command=self.remove_contact)
        self.remove_button.grid(row=4, column=0, columnspan=2)
        
        self.tree = ttk.Treeview(root, columns=("Name", "Phone"), show='headings')
        self.tree.heading("Name", text="Name")
        self.tree.heading("Phone", text="Phone")
        self.tree.column("Name", width=150)
        self.tree.column("Phone", width=150)
        self.tree.grid(row=5, column=0, columnspan=2)
        self.update_contacts_treeview()
        
        self.tree.bind('<<TreeviewSelect>>', self.load_selected_contact)
        
    def load_contacts(self):
        if not os.path.exists("contact_book.txt"):
            return []
        with open("contact_book.txt", "r") as f:
            contacts = [line.strip() for line in f.readlines()]
        print(contacts)
        return contacts

    
    def save_contacts(self):
        with open("contact_book.txt", "w") as f:
            for contact in self.contacts:
                f.write(contact + "\n")
    
    def add_contact(self):
        name = self.name_entry.get()
        phone = self.phone_entry.get()
        if not name or not phone:
            messagebox.showwarning("Input Error", "Please enter both name and phone number")
            return
        contact = f"{name}: {phone}"
        self.contacts.append(contact)
        self.save_contacts()
        self.update_contacts_treeview()
        self.name_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
    
    def update_contacts_treeview(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for contact in self.contacts:
            name, phone = contact.split(": ")
            self.tree.insert("", tk.END, values=(name, phone))
    
    def load_selected_contact(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        contact = self.tree.item(selected_item)["values"]
        name, phone = contact
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(tk.END, name)
        self.phone_entry.delete(0, tk.END)
        self.phone_entry.insert(tk.END, phone)
    
    def update_contact(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a contact to update")
            return
        name = self.name_entry.get()
        phone = self.phone_entry.get()
        if not name or not phone:
            messagebox.showwarning("Input Error", "Please enter both name and phone number")
            return
        contact = f"{name}: {phone}"
        index = self.tree.index(selected_item)
        self.contacts[index] = contact
        self.save_contacts()
        self.update_contacts_treeview()
        self.name_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
    
    def remove_contact(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a contact to remove")
            return
        index = self.tree.index(selected_item)
        self.contacts.pop(index)
        self.save_contacts()
        self.update_contacts_treeview()
        self.name_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ContactBook(root)
    root.mainloop()
