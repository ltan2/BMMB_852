## Name: Linai Tan

### Proof of computer setup
![pixi](images/bioinfo_and_stats.png)
![git](images/git_version.png)

### AI code editor
##### VSCode

![VScode](images/vscode_codex.png)

### Github account
https://github.com/ltan2/BMMB_852.git

### Create dir and README
```bash
mkdir week1_hw # create dir
touch week1_hw/README.md # create file
```
![git](images/dir_file.png)


### samtools version
```bash
samtools --version
```
![samtools](images/samtools.png)

### Create nested directory and file
```bash
mkdir -p week1_hw/demo # create parent and child dir
touch week1_hw/demo/hello.txt # create file
```
![nested_dir_file](images/nested_dir_file.png)

### Create files in different directory
```bash
touch week1_hw/hello.txt # create in week1_hw dir
touch hello.txt # create in curr dir
```
![diff_dir_files](images/diff_dir_files.png)

### Access file in relative and absolute path
```bash
pwd
/Users/linaitan/BMMB_852

cat week1_hw/demo/hello.txt # print contents of file from relative path
cat /Users/linaitan/BMMB_852/week1_hw/demo/hello.txt # print contents of file from absolute path
```

#### Output:
![abs_relative](images/abs_relative.png)
