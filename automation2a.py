# SECOND STAGE: Adding Molecules to Fill the Crystal Structure

import subprocess
import time
from shutil import copyfile
import os
import io
import sys

file='mTIP'
residue='TIPS'
jobname='TIPS'

def check_run_status():
    time.sleep(10)
    read_file=open('./automation.out')
    for i, line in enumerate(read_file):
        job_id=line.split()[3]
    check_status='squeue -h -j '+ str(job_id)
    process=subprocess.run(check_status, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
    output = process.stdout
    while output.__contains__(job_id):
        time.sleep(10)
        process=subprocess.run(check_status, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
        output = process.stdout
    return True

def no_molecule(file,res):
    filepath=os.getcwd()+'/'+str(file)+'.gro'
    a_file=open(filepath, 'r')
    lines=a_file.readlines()
    first=lines[2].split()[0].split(res)[0]
    last=lines[-2:-1][0].split()[0].split(res)[0]
    number=int(last)-int(first)+1
    return number

def top(file, no_mol,res):
   filepath='./'+str(file)+'.top'
   copyfile('./standard.top', './'+filepath)
   hs = open('./'+filepath,'a')
   txt=res+'   '+str(no_mol)
   hs.write(txt)
   hs.close()


def make_sh_file1(code):
    sh= open('./compile.sh','w')
    sh.write('module load gromacs/gromacs-2021.2'+'\n')
    sh.write(code)
    sh.close()
    filename = './gromacs.err'
    with io.open(filename, 'wb') as writer, io.open(filename, 'rb', 1) as reader:
        process = subprocess.Popen('source compile.sh'+'; env -0',shell=True, executable='/bin/bash',stdout=writer)
        while process.poll() is None:
            sys.stdout.write(str(reader.read()))
            time.sleep(5)
        sys.stdout.write(str(reader.read()))

def make_sh_file(code):
    sh= open('./compile.sh','w')
    sh.write('module load gromacs/gromacs-2021.2'+'\n')
    sh.write(code)
    sh.close()
    filename = './gromacs.err'
    output = subprocess.check_output('source compile.sh'+'; env -0',shell=True, executable='/bin/bash')

def compilee(txt,job):
   copyfile('./compile.sh', './'+job)
   hs = open('./'+job,'a')
   hs.write(txt)
   hs.close()
   subprocess.run(['sbatch', './'+job])
   time.sleep(5)
   done=check_run_status()
   hs = open('./gromacs.err','r')
   for i, line in enumerate(hs):
       if line=='Fatal error:':
           raise SystemExit

def run(txt,job):
   copyfile('./run.sh', './'+job)
   hs = open('./'+job,'a')
   hs.write(txt)
   hs.close()
   subprocess.run(['sbatch', './'+job])
   time.sleep(10)
   done=check_run_status()
   hs = open('./gromacs.err','r')
   for i, line in enumerate(hs):
       if line=='Fatal error:':
           raise SystemExit
       if line=='Error in user input:':
           raise SystemExit

def howmanyadded():
    hs = open(jobname+'.err','r')
    for i, line in enumerate(hs):
        if 'Added' in line:
            addedm = int(line.split()[1])
    return addedm

for i in range(5):
    no_mol=no_molecule(file,residue)
    top(file, no_mol,residue)
    time.sleep(5)
    make_sh_file('gmx_mpi grompp -f minim.mdp -c '+file+'.gro -r '+file+'.gro -p '+file+'.top -o em.tpr -maxwarn 4')
    time.sleep(5)
    make_sh_file('mpirun gmx_mpi mdrun -v -deffnm em -ntomp 1')
    time.sleep(5)
    make_sh_file('gmx_mpi grompp -f nvt3.mdp -c em.gro -r em.gro -p '+file+'.top -o nvt3.tpr -maxwarn 3')
    time.sleep(5)
    make_sh_file('mpirun gmx_mpi mdrun -v -deffnm nvt3 -ntomp 1')
    time.sleep(5)
    make_sh_file('gmx_mpi insert-molecules -f nvt3.gro -ci '+residue+'.gro -nmol 10000 -rot xyz -o '+file+'.gro')
    time.sleep(5)
