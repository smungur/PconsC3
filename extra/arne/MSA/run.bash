#!/bin/bash -x
#SBATCH -A snic2015-10-12 
# We actually start 6 jobs in parallel.
# Probably more efficient than running with 5 thread.
#SBATCH -n 6 
#SBATCH -c 1 
#SBATCH --time=04:00:00 
#SBATCH -J RunJackhmmer 
#SBATCH --output=out/PconsC3.%J.out
#SBATCH --error=err/PconsC3.%J.err 

for i in "$@"
do
    if [ -s $i.JH0.001.trimmed ]
    then
	i=$i.JH0.001.trimmed
    fi
    k=`basename $i .fa`
    l=`basename $k .fasta`
    j=`basename $l .trimmed`
    m=`echo $j | sed "s/.fasta.*//"`
    n=$m.fasta
    if  [ -s $n ]
    then
	echo "Using $n"
    else
	m=`echo $j | sed "s/\.fa\..*//"`
	n=$m.fa
	if  [ -s $n ]
	then
	    echo "Using $n"
	else
	    echo "ERROR: Not found FASTa file $i $m $n"
	    exit 0
	fi
    fi
    
    shorttime="06:00:00"
    longtime="24:00:00"
    mem="120GB"
    
    if [ ! -s $j.trimmed ] && [ ! -s $i.JH0.001.trimmed  ]
    then
	if [ -s $j.a3m ]
	then
	    ~/git/PconsC3/extra/arne/MSA/a3mToTrimmed.py $j.a3m > $j.trimmed
	elif [ -s $j.JH0.001.a3m ]
	then
	    ~/git/PconsC3/extra/arne/MSA/a3mToTrimmed.py $j.JH0.001.a3m > $j.JH0.001.trimmed 

	else
	     	     ~/git/PconsC3/extra/arne/MSA/runjackhmmer.py $i > $j-runjackhmmer.out 
	fi
    else
# #    if [ !  -s $k.out ]
# #    then
# #     	~/git/PconsC3/extra/arne/MSA/run_PconsC3.bash  $i > $j.out &
# #    fi
	length=`head -2 $j.trimmed | wc -c `
	
	if [ $length -gt 500 ] 
	then
	    minitime="01:00:00"
	    shorttime="08:00:00"
	    longtime="48:00:00"
	    mem="120GB"
	else
	    minitime="00:15:00"
	    shorttime="04:00:00"
	    longtime="12:00:00"
	    mem="64GB"
	fi

	if [ !  -s $j.rr ] && [ ! -s $m.rr ]
	then
            $HOME/git/PconsC3/extra/arne/MSA/runPhyCMAP.bash $n 
	fi
#	if [ !  -s $m.rsa ]
#	then
#            $HOME/git/PconsC3/extra/arne/MSA/runnetsurfp.py $n 
#	fi
	if [ !  -s $j.ss2 ] && [ -s $j.trimmed  ]
	then
            $HOME/git/PconsC3/extra/arne/MSA/addss.pl $i 
	fi
	if [ !  -s $j.gdca ] && [ -s $j.trimmed  ]
	then
            $HOME/git/PconsC3/rungdca.py $i 
	fi
	if [ !  -s $j.0.02.plm20 ]
	then
            $HOME/git/PconsC3/runplm.py $i 
	fi
	if [ ! -s $j.rr ] && [ -s $m.rr ]
	then
	    ln -s $m.rr $j.rr 
	fi
	if [ ! -s $j.fa.rsa ] && [ -s $m.rsa ]
	then
	    ln -s $m.rsa $j.fa.rsa 
	fi
	
	if [ !  -s $j.PconsC3.l5 ] && [ -s $j.trimmed ]
	then
  	    if [ -s $j.gdca ]  && [ -s $j.0.02.plm20 ]   && [ -s $j.rr ]  && [ -s $j.fa.rsa ]  && [ -s  $j.ss2 ] && [ -s  $j.gneff ]  && [ -s $j.trimmed ]
  	    then
		if [ $length -lt 200 ] 
		then
#		    time $HOME/git/PconsC3/predict.py $j.gdca $j.0.02.plm20 $j.rr $j.fa.rsa $j.ss2 $j.gneff $j.trimmed $HOME/git/PconsC3/ -1 $j.PconsC3  
		    time $HOME/git/PconsC3/predict-queue.py $j.gdca $j.0.02.plm20 $j.rr $j.fa.rsa $j.ss2 $j.gneff $j.trimmed $HOME/git/PconsC3/ -1 4 $j.PconsC3
		    #		time $HOME/git/PconsC3/predict-simultaneous.py $j.gdca $j.0.02.plm20 $j.rr $j.fa.rsa $j.ss2 $j.gneff $j.trimmed $HOME/git/PconsC3/ -1 $j.PconsC3
		fi
  	    else 
  		ls -l $j.gdca $j.0.02.plm20 $j.rr $j.fa.rsa $j.ss2 $j.gneff $j.trimmed 
  	    fi
	fi
    fi
done
