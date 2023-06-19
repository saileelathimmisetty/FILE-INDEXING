import time
import datetime
class FileNode:
    def __init__(self, name, is_directory=False):
        self.name = name
        self.is_directory = is_directory
        self.children = []
        self.size = 0
        self.last_modified = None
        self.hash = None


class HashTree: #grp
    def __init__(self, node=None):
        self.root = node

    def calculate_hash(self, data):
        hash_value = 0
        for char in data:
            hash_value += ord(char)
        return str(hash_value)

    def construct_tree(self, node):
        if not node:
            return None

        if not node.is_directory:
            node.hash = self.calculate_hash(f"{node.name}{node.size}")
            return node.hash

        child_hashes = []
        for child in node.children:
            child_hash = self.construct_tree(child)
            child_hashes.append(child_hash)

        node.hash = self.calculate_hash("".join(child_hashes))
        return node.hash


class FileSystemTree:
    def __init__(self):
        self.root = FileNode("/")
        self.size_index = {}
        self.hash_index = {}

    def add_file(self, path, size): #gk
        components = path.strip("/").split("/")
        current_node = self.root

        for component in components[:-1]:
            found = False
            for child in current_node.children:
                if child.name == component and child.is_directory:
                    current_node = child
                    found = True
                    break

            if not found:
                new_node = FileNode(component, is_directory=True)
                current_node.children.append(new_node)
                current_node = new_node

        file_name = components[-1]
        file_node = FileNode(file_name)
        file_node.size = size
        file_node.last_modified = time.time()
        current_node.children.append(file_node)

        if size in self.size_index:
            self.size_index[size].append(file_node)
        else:
            self.size_index[size] = [file_node]

        hash_tree = HashTree()
        hash_tree.construct_tree(self.root)
        self.hash_index[file_node.hash] = file_node

    def get_node(self, path):
        components = path.strip("/").split("/")
        current_node = self.root

        for component in components:
            found = False
            for child in current_node.children:
                if child.name == component:
                    current_node = child
                    found = True
                    break

            if not found:
                return None

        return current_node

    def sort_files(self):
        for files in self.size_index.values():
            files.sort(key=lambda file: file.name)

    def new_directory(self, path, directory_name):
        parent_node = self.get_node(path)
        if parent_node and parent_node.is_directory:
            new_directory_node = FileNode(directory_name, is_directory=True)
            parent_node.children.append(new_directory_node)
            parent_node.last_modified = time.time()
            return True
        return False

    def get_files_above_size(self, size):  #dhaya
        result = []
        for file_size, files in self.size_index.items():
            if file_size > size:
                result.extend(files)
        return result

    def rename_file(self, path, new_name):
        node = self.get_node(path)
        if node:
            node.name = new_name
            node.last_modified = time.time()
        else:
            print("File not found.")

    def open_directory(self, directory_path, file_name, file_size): #dhaya
        directory_node = self.get_node(directory_path)
        if directory_node and directory_node.is_directory:
            new_file_node = FileNode(file_name)
            new_file_node.size = file_size
            directory_node.children.append(new_file_node)
            directory_node.last_modified = time.time()
            if file_size in self.size_index:
                self.size_index[file_size].append(new_file_node)
            else:
                self.size_index[file_size] = [new_file_node]
            hash_tree = HashTree()
            hash_tree.construct_tree(self.root)
            self.hash_index[new_file_node.hash] = new_file_node
            return True
        return False

    def print_files_in_directory(self, directory_path):
        directory_node = self.get_node(directory_path)
        if directory_node and directory_node.is_directory:
            print(f"Files in directory: {directory_path}")
            for child in directory_node.children:
                if not child.is_directory:
                    print(child.name)
        else:
            print(f"Directory not found: {directory_path}")

    def calculate_directory_size(self, directory_path):
        directory_node = self.get_node(directory_path)
        if directory_node and directory_node.is_directory:
            total_size = 0
            for child in directory_node.children:
                if child.is_directory:
                    total_size += self.calculate_directory_size(directory_path + "/" + child.name)
                else:
                    total_size += child.size
            return total_size
        else:
            return 0

    def construct_adjacency_list(self, node):
        adjacency_list = []
        for child in node.children:
            adjacency_list.append(child.name)  # Add child node name to adjacency list
            adjacency_list.extend(self.construct_adjacency_list(child))  # Recursively build adjacency list for child nodes
        return adjacency_list

    def visualize_adjacency_list(self):
        adjacency_list = self.construct_adjacency_list(self.root)
        print("File System Tree (Adjacency List):")
        for i, node in enumerate(adjacency_list):
            print(f"{i}: {node}")
            
    def delete_file(self, file_path):
        file_node = self.get_node(file_path)

        if file_node and file_node.is_directory:
            print("Cannot delete a directory.")
            return

        if not file_node:
            print("File not found.")
            return

        parent_directory_node = self.get_node("/".join(file_path.split("/")[:-1]))
        parent_directory_node.children.remove(file_node)
        parent_directory_node.last_modified = time.time()

        file_size = file_node.size
        if file_size in self.size_index:
            self.size_index[file_size].remove(file_node)

        if file_node.hash in self.hash_index:
            del self.hash_index[file_node.hash]

        print(f"File '{file_node.name}' deleted successfully.")

    def move_file(self, source_path, destination_path):
        source_node = self.get_node(source_path)
        destination_node = self.get_node(destination_path)

        if source_node and source_node.is_directory:
            print("Cannot move a directory.")
            return

        if not source_node:
            print("Source file not found.")
            return

        if not destination_node or not destination_node.is_directory:
            print("Destination directory not found.")
            return

        source_directory_node = self.get_node("/".join(source_path.split("/")[:-1]))
        source_directory_node.children.remove(source_node)
        source_directory_node.last_modified = time.time()

        destination_node.children.append(source_node)
        destination_node.last_modified = time.time()

        print(f"File '{source_node.name}' moved successfully.")

        hash_tree = HashTree()
        hash_tree.construct_tree(self.root)
        self.hash_index[source_node.hash] = source_node


    def sort_files_by_last_modified(self):
        sorted_files = []

        for files in self.size_index.values():
            sorted_files.extend(files)

        sorted_files = [file for file in sorted_files if file and hasattr(file, "last_modified")]

        sorted_files.sort(key=lambda file: file.last_modified if hasattr(file, "last_modified") else 0 if file.last_modified is not None else float('inf'))

        for file in sorted_files:
            last_modified_time = datetime.datetime.fromtimestamp(file.last_modified)
            formatted_time = last_modified_time.strftime("%H:%M")  # Update the format to "%H:%M"
            print(f"Name: {file.name}, Last Modified: {formatted_time}")

        return sorted_files

            

    def list_directory_contents(self, directory_path):  #dhaya
        directory_node = self.get_node(directory_path)
        if directory_node and directory_node.is_directory:
            print(f"Contents of directory: {directory_path}")
            for child in directory_node.children:
                print(child.name)
        else:
            print(f"Directory not found: {directory_path}")



def display_menu():
    print("Menu:")
    print("1. List directory contents")
    print("2. Add file")
    print("3. Create new directory")
    print("4. Rename file")
    print("5. Sort files by last modified")
    print("6. Calculate directory size")
    print("7. Open directory")
    print("8. Get files above size")
    print("9. Delete file")
    print("10. Move file")
    print("11. Visualize file system tree") 
    print("0. Exit")



def main():
    fs = FileSystemTree()

    while True:
        display_menu()
        choice = input("Enter your choice: ")

        if choice == "1":
            print("Press 'b' to go back")
            txt = input()
            if txt=="b":
                continue
            directory_path = input("Enter the directory path: ")
            fs.list_directory_contents(directory_path)
        elif choice == "2":
            print("Press 'b' to go back")
            txt = input()
            if txt=="b":
                continue
            file_path = input("Enter the file path: ")
            file_size = int(input("Enter the file size: "))
            fs.add_file(file_path, file_size)
        elif choice == "3":
            print("Press 'b' to go back")
            txt = input()
            if txt=="b":
                continue
            directory_path = input("Enter the parent directory path: ")
            directory_name = input("Enter the new directory name: ")
            fs.new_directory(directory_path, directory_name)
        elif choice == "4":
            print("Press 'b' to go back")
            txt = input()
            if txt=="b":
                continue
            file_path = input("Enter the file path: ")
            new_name = input("Enter the new file name: ")
            fs.rename_file(file_path, new_name)
        elif choice == "5":
            print("Press 'b' to go back")
            txt = input()
            if txt=="b":
                continue
            print("Files sorted by last modified timestamp:")
            fs.sort_files_by_last_modified()
        elif choice == "6":
            print("Press 'b' to go back")
            txt = input()
            if txt=="b":
                continue
            directory_path = input("Enter the directory path: ")
            directory_size = fs.calculate_directory_size(directory_path)
            print(f"Size of '{directory_path}': {directory_size} bytes")
        elif choice == "7":
            print("Press 'b' to go back")
            txt = input()
            if txt=="b":
                continue
            directory_path = input("Enter the directory path: ")
            file_name = input("Enter the new file name: ")
            file_size = int(input("Enter the file size: "))
            fs.open_directory(directory_path, file_name, file_size)
        elif choice == "8":
            print("Press 'b' to go back")
            txt = input()
            if txt=="b":
                continue
            size = int(input("Enter the size: "))
            files_above_size = fs.get_files_above_size(size)
            print(f"Files above size {size} bytes:")
            for file in files_above_size:
                print(f"Name: {file.name}, Size: {file.size}")
        elif choice == "9":
            print("Press 'b' to go back")
            txt = input()
            if txt=="b":
                continue
            file_path = input("Enter the file path: ")
            fs.delete_file(file_path)
        elif choice == "10":
            print("Press 'b' to go back")
            txt = input()
            if txt=="b":
                continue
            source_path = input("Enter the source file path: ")
            destination_path = input("Enter the destination directory path: ")
            fs.move_file(source_path, destination_path)
        elif choice == "11":
            fs.visualize_adjacency_list()
        elif choice == "0":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")
        print()

if __name__ == "__main__":
    main()