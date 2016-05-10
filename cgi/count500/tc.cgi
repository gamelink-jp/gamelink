#!/usr/bin/perl
#
######################################################################
###
###
###  CGI�J�E���^�[ TcounT Ver.5.03
###     [1/2] �{�� (tc.cgi)
###                                 (c) 1996-2004 Takahiro Nishida
###                                 http://www.mytools.net/
###
###
######################################################################
#
### �ϐ��ݒ蕔 �i�ڍׂ͏�L�y�[�W�������������j ######################

# �f�[�^�t�@�C���i�[�ʒu
$basedir = ".";
# �����C��
$time_fix = 0;

### �ϐ��ݒ蕔 �i�����܂Łj###########################################

# �ő包���i�J�E���^�����h�~�j
$MAX_KETA_NUM = 20;


$lockfile = "$basedir/lockdir/tc.lock";
$allfile = "$basedir/tcdall.txt";
$ystfile = "$basedir/tcdyst.txt";
$hstfile = "$basedir/tcdhst.txt";
$logfile = "$basedir/tcdlog.txt";
$bakfile = "$basedir/tcdbak.txt";


require './gifcat.pl';

&main;



##### ���C��
sub main
{
	&get_input;
	&lock;
	&open_datafile;
	if($m_incr)
	{
		&check_date;
		&increase_counter;
	}
	&unlock;
	&get_count;
	&show_counter;
}



##### ���͂̎擾
sub get_input
{
	$buffer = $ENV{'QUERY_STRING'};
	@m_prm = split("&", $buffer);
	
	$m_name = ($m_prm[0] =~ /^\w+$/) ? $m_prm[0] : ''   ;
	$m_type = ($m_prm[1] =~ /^\w+$/) ? $m_prm[1] : 'a'  ;
	$m_incr = ($m_prm[2] == 1)       ? 1         :  0   ;
	$m_gazo = ($m_prm[3] =~ /^\w+$/) ? $m_prm[3] : 'img';
	$m_keta = ($m_prm[4])            ? $m_prm[4] :  5   ;
	
	# �J�E���^�����w�肳��Ă��Ȃ��ƃG���[
	($m_name) || &error(101, "�J�E���^�[�����w�肳��Ă��܂���");
	# <gazo>�f�B���N�g�����Ȃ��ƃG���[
	(-d "$basedir/$m_gazo") || &error(102, "�摜�f�B���N�g��($m_gazo)������܂���");
	
	# �z�X�g
	$remote_host = $ENV{'REMOTE_HOST'} || &nslook($ENV{'REMOTE_ADDR'}) || $ENV{'REMOTE_ADDR'};
}



##### �e��f�[�^�t�@�C�����J��
sub open_datafile
{
	### �����t�@�C��
	open(FILE, $allfile) || &error(111, "�t�@�C�� tcdall.txt ���J���܂���");
	@tdys = <FILE>;
	close(FILE);
	
	### �N���b�V�����J�o��
	($tdys[0]) || &recover_counter;
	
	### �O��̋L�^���t
	$date_rec = $tdys[0] || "00000000\n";
	chop($date_rec);
	
	### �Ώۃ��R�[�h����
	$g_rno = -1;
	foreach(@tdys)
	{
		$g_rno++;
		(/^$m_name\t/) || next;
		($tmp, $g_a, $g_ah) = split("\t");
		last;
	}
	defined($g_a) || &error(112, "�J�E���^�� $m_name �͐ݒ肳��Ă��܂���");
}



##### ���v�̎擾
sub check_date
{
	# �����t���O������ꍇ�̂ݔ�������s �� (030806)main�Ɉڍs
#	($m_incr) || return;
	
	# ���t���ς���Ă��邩�`�F�b�N
	($tmp, $tmp, $tmp, $mday, $mon, $year) = localtime(time() + 60 * 60 * $time_fix);
	$mon++;
	$year += 1900;
	$date_now = sprintf("%04d%02d%02d", $year, $mon, $mday);
	
	# ���t���ς���Ă��Ȃ�������߂�
	($date_now > $date_rec) || return;
	
	##### �ȉ��T�}���쐬��
	&update_summery;
}



##### �J�E���g�A�b�v
sub increase_counter
{
	# �����t���O�������̏ꍇ�̂ݎ��s �� (030806)main�Ɉڍs
#	($m_incr && $m_type =~ /a/) || return;
	
	# �����J�E���g�A�b�v�i�Ƃ肠���������j
	$g_a++;
	$g_ah++;
	
	# �z�X�g�d���`�F�b�N
	open(FILE, $bakfile) || &error(121, "�t�@�C�� tcdbak.txt ���J���܂���");
	foreach(<FILE>)
	{
		(/\t$m_name\t$remote_host\t/) || next;
		# �d�����Ă���߂�
		$g_ah--;
		last;
	}
	close(FILE);
	
	# �V�����s�̍쐬
	$tdys[$g_rno] = "$m_name\t$g_a\t$g_ah\t\n";
	
	# �t�@�C���̍X�V
	open(FILE, ">$allfile") || &error(122, "�t�@�C�� tcdall.txt �ɏ������߂܂���");
	print FILE @tdys;
	close(FILE);
	
	# ���O�̋L�^
	($sec, $min, $hour) = localtime(time() + 60 * 60 * $time_fix);
	$accesstime = sprintf("%02d:%02d:%02d", $hour, $min, $sec);
	open(FILE, ">>$bakfile") || &error(123, "�t�@�C�� tcdbak.txt ���J���܂���");
	print FILE "$accesstime\t$m_name\t$remote_host\t\n";
	close(FILE);
}



##### �\�����ׂ��l�̎擾
sub get_count
{
	### ����
	if($m_type eq "a"){
		$g_shownum = $g_a;
	}
	### �����z�X�g
	elsif($m_type eq "ah"){
		$g_shownum = $g_ah;
	}
	else
	{
		### ����t�@�C�����J��
		open(FILE, $ystfile) || &error(131, "�t�@�C�� tcdyst.txt ���J���܂���");
		foreach(<FILE>)
		{
			(/^$m_name\t/) || next;
			($tmp, $b_y, $b_yh, $b_ty, $b_tyh) = split("\t");
			last;
		}
		close(FILE);
		### ���
		if($m_type eq "y"){
			$g_shownum = $b_y;
		}
		### ����z�X�g
		elsif($m_type eq "yh"){
			$g_shownum = $b_yh;
		}
		### ����
		elsif($m_type eq "t"){
			$g_shownum = $g_a - $b_ty;
		}
		### �����z�X�g
		elsif($m_type eq "th"){
			$g_shownum = $g_ah - $b_tyh;
		}
		else{
			&error(132, "TYPE $m_type �͑��݂��܂���");
		}
	}
}



##### �J�E���^�[�摜�̕\��
sub show_counter
{
	@nums = split("", $g_shownum);
	(@nums > $MAX_KETA_NUM) && &error(141, "���������($MAX_KETA_NUM)�𒴂��Ă��܂��B�\���ł��܂���B");
	
	while(@nums < $m_keta){
		unshift(@nums, "0");
	}
	
	for(0..$#nums){
		$nums[$_] = "$basedir/$m_gazo/$nums[$_].gif";
	}
	
	print "Content-type: image/gif\n\n";
	binmode(STDOUT);
	$| = 1;
	print &gifcat'gifcat(@nums);
}



##### �����������Ƃ��̏���
sub update_summery
{
	
	### ���v�J�n���O
	&writelog("Date has changed. Create summery start.");
	
	### ���t�X�V
	$tdys[0] = "$date_now\n";
	
	### ����t�@�C�����J���ăn�b�V����
	open(FILE, $ystfile) || &error(151, "�t�@�C�� tcdyst.txt ���J���܂���");
	foreach(<FILE>)
	{
		($b_name, $b_y, $b_yh, $b_ty, $b_tyh) = split("\t");
		$HTIY{$b_name} = $b_ty;
		$HTIH{$b_name} = $b_tyh;
	}
	close(FILE);
	
	### ���v�ƐV��������t�@�C���̍쐬
	$b_newhst = "$date_rec\t";
	foreach(@tdys)
	{
		(/\t/) || next;
		($b_name, $b_a, $b_ah) = split("\t");
		$b_tdy  = $b_a  - $HTIY{$b_name};
		$b_tdyh = $b_ah - $HTIH{$b_name};
		### ���v
		$b_newhst .= "$b_name/$b_tdy/$b_tdyh/$b_a/$b_ah\t";
		### ����t�@�C��
		$b_newyst .= "$b_name\t$b_tdy\t$b_tdyh\t$b_a\t$b_ah\t\n";
	}
	$b_newhst .= "\n";
	
	### ���v�̋L�^
	open(FILE, ">>$hstfile") || &error(152, "�t�@�C�� tcdhst.txt �ɏ������߂܂���");
	print FILE $b_newhst;
	close(FILE);
	
	### ����t�@�C���̏�������
	open(FILE, ">$ystfile") || &error(153, "�t�@�C�� tcdyst.txt �ɏ������߂܂���");
	print FILE $b_newyst;
	close(FILE);
	
	### �o�b�N�A�b�v�t�@�C���̃N���A
	open(FILE, ">$bakfile") || &error(154, "�t�@�C�� tcdbak.txt �ɏ������߂܂���");
	close(FILE);
	
	### ���샍�O�t�@�C���̃N���A
	open(FILE, ">$logfile") || &error(155, "�t�@�C�� tcdlog.txt �ɏ������߂܂���");
	close(FILE);
	
	### ���v�J�n���O
	&writelog("Create summery finish.");
}



##### ���J�o���[
sub recover_counter
{
	### ���J�o���J�n
	&writelog("Datafile crash has detected. Start recovery.");
	
	### ����܂ł̌������擾
	open(FILE, $ystfile) || &error(161, "�t�@�C�� tcdyst.txt ���J���܂���");
	foreach(<FILE>)
	{
		($b_name, $b_y, $b_yh, $b_ty, $b_tyh) = split("\t");
		$HA{$b_name} = $b_ty;
		$HAH{$b_name} = $b_tyh;
		push(@order, $b_name);
	}
	close(FILE);
	
	### �o�b�N�A�b�v��ǂ݂J�E���g����
	open(FILE, $bakfile) || &error(162, "�t�@�C�� tcdbak.txt ���J���܂���");
	foreach(<FILE>)
	{
		($tmp, $b_name, $b_host) = split("\t");
		$HA{$b_name}++;
		($HHOST{$b_host}) && next;
		$HAH{$b_name}++;
		$HHOST{$b_host} = 1;
	}
	close(FILE);
	
	##### �u�O���v�̎擾
	($tmp, $tmp, $tmp, $mday, $mon, $year) = localtime(time() + 60 * 60 * $time_fix);
	$mon++;
	$year += 1900;
	$date_yst = sprintf("%04d%02d%02d", $year, $mon, $mday);
	
	### �����f�[�^�̍č쐬
	$i = 0;
	$tdys[0] = "$date_yst\n";
	foreach(@order){
		$tdys[++$i] = "$_\t$HA{$_}\t$HAH{$_}\t\n";
		&writelog("$_: Recovered to a=$HA{$_}, ah=$HAH{$_}");
	}
	
	### �����t�@�C���̍č쐬
	open(FILE, ">$allfile") ||  &error(163, "�t�@�C�� tcdall.txt �ɏ������߂܂���");
	print FILE @tdys;
	close(FILE);
	
	&writelog("Recovery has been finished.");
	
	&error(164, "�J�E���^�̃��J�o�[�^���������������܂����B");
}



##### ���O�L�^
sub writelog
{
	local($msg) = @_;
	
	($sec, $min, $hour, $mday, $mon, $year) = localtime(time() + 60 * 60 * $time_fix);
	$mon++;
	$year += 1900;
	$logtime = sprintf("%04d/%02d/%02d %02d:%02d:%02d", $year, $mon, $mday, $hour, $min, $sec);
	
	open(FILE, ">>$logfile") || &error(171, "�t�@�C�� tcdlog.txt �ɏ������߂܂���");
	print FILE "$logtime $msg\n";
	close(FILE);
}



##### IP����HOST�擾
sub nslook
{
	local($ip) = @_;
	$ip =~ /([0-9]+)\.([0-9]+)\.([0-9]+)\.([0-9]+)/;
	return gethostbyaddr(pack('C4', $1, $2, $3, $4), 2);
}



##### �t�@�C�����b�N
sub lock
{
	local($try) = 10;
	while(!(mkdir($lockfile, 0700))){
		if(--$try > 0){
			&writelog("$m_name: Locking.");
			&error(100, "���b�N���ł�");
		}
		sleep(1);
	}
}



##### ���b�N����
sub unlock
{
	rmdir($lockfile);
}



##### �G���[�\��
sub error
{
	local($id, $errmsg) = @_;
	local(@sts) = lstat($lockfile);
	local($tn) = time();
	
	print "Content-type: text/plain\n\n";
	print "Error (Code:$id) - $errmsg";
	
	($id == 100) || &unlock; # ID �� 100 �ȊO�̏ꍇ�̓��b�N����
	($tn - $sts[9] < 15) || &unlock; # ��15�b�ȏネ�b�N�������Ă��玩������
	exit;
}
