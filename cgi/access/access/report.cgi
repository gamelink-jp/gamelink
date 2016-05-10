#!/usr/bin/perl

#=====================================================================
# access cgi �A�N�Z�X���擾�t�@�C�� report.cgi (2002/05/19)
#---------------------------------------------------------------------
# Original Script
#	Access Report v2.21 (2002/02/04)
#	�A�N�Z�X��̓V�X�e��
#	Copyright(C) Kent Web 2002
#	webmaster@kent-web.com
#	http://www.kent-web.com/
#---------------------------------------------------------------------
# modified by himura
#	access cgi ver.2.12 (2002/05/19)
#	mail�F himura@dolphin.plala.or.jp
#	site�F http://air.vis.ne.jp/at-works/
#---------------------------------------------------------------------
$ver = 'Access Report v2.21';
$acver = 'access cgi ver.2.12';
#---------------------------------------------------------------------
# �f�[�^�\��
#	���O�F"NO , DATE , REF , USER_AGENT , PIXEL , HOST , ADDR , DOC , "
#	���ʁF"DATES , ACCESS , "
#=====================================================================
# ���ݒ�

# ���ʐݒ�t�@�C���捞
require './common.ini';

# ���b�N�t�@�C���ݒ�
$lock_dir = './lock/';
$lockfile = "$lock_dir".'report.lock';

#---------------------------------------------------------------------

# cookie ����
$cookie_admin = 'access';

# cookie ��������
$cookie_del = '30';

#---------------------------------------------------------------------

# ���{��f�R�[�h���O�i�����T�[�r�X�� UTF-8 ���j
@nodecode = (
	'search.msn.*results.asp?',
	'google.*search?*e=utf8',
	'google.*search?*e=utf-8',
	'lycos.co.jp?*ie=utf-8',
);

#=====================================================================
# ����

# QUERY_STRING �̃`�F�b�N
if ($ENV{'QUERY_STRING'} eq 'check') { &check; }

# REQUEST_METHOD �̃`�F�b�N
if ($ENV{'REQUEST_METHOD'} eq "POST") { &stop; }

#---------------------------------------------------------------------
# HTTP_REFERER �� QUERY_STRING ���擾���ăf�R�[�h

$httpref = $ENV{'HTTP_REFERER'};
$query   = $ENV{'QUERY_STRING'};

$decode ='';
if ($httpref) {

	$decode = 1;
	$httpref =~ tr/+/ /;
	foreach (@nodecode) {
		if ($_ eq '') { next; }
		$_ =~ s/\?/\\?/g;
		$_ =~ s/\+/\\+/g;
		$_ =~ s/\*/\.\*/g;
		if ($httpref =~ /$_/i) { $decode = ''; }
	}
	if ($decode) { $httpref =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg; }
	$httpref =~ s/</&lt;/g;
	$httpref =~ s/>/&gt;/g;
	$httpref =~ tr/\r\n//d;
}

unless ($ssi_mode) {

	$decode ='';
	if ($query) {
		$decode = 1;
		$query =~ tr/+/ /;
		foreach (@nodecode) {
			if ($_ eq '') { next; }
			$_ =~ s/\?/\\?/g;
			$_ =~ s/\+/\\+/g;
			$_ =~ s/\*/\.\*/g;
			if ($query =~ /$_/i) { $decode = ''; }
		}
		if ($decode) { $query =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg; }
		$query =~ s/</&lt;/g;
		$query =~ s/>/&gt;/g;
		$query =~ tr/\r\n//d;
	}

}

#---------------------------------------------------------------------
# �f�B���N�g���I�����Ɖ𑜓x�ƃ����N�����擾

$logdir_data = $pixel = $ref = '';

if ($ssi_mode) {

# <!--#include virtual="***/report.cgi?default"-->

	$logdir_data = $ARGV[0];
	$ref         = $httpref;

} else {

# report.cgi?dir=default&pix=***&ref=**

	@pairs = split(/&/, $query, 3);
	foreach $pair (@pairs){
		($name, $value) = split(/=/, $pair, 2);
		$FORM{$name} = $value;
	}

	$logdir_data = $FORM{'dir'};
	$pixel       = $FORM{'pix'};
	$ref         = $FORM{'ref'};

# �𑜓x���g����x�����h�ȊO�̏ꍇ�͋󗓂ɂ���
	if ($pixel =~ /(\d+)x(\d+)/) { $pixel = "$1x$2"; } else { $pixel = ''; }

}

#---------------------------------------------------------------------
# �f�B���N�g���ݒ�擾

unless ($logdir_data) { $logdir_data = $default_ini; }

foreach (@log_dir) {
	if ($_ eq '') { next; }
	($key, $value) = split(/<>/, $_);
	if ($logdir_data eq $key) { $logdir = $value; last; }
}

$iniadd = "$logdir"."$iniadd";
$checkpl = "$logdir"."$checkpl";
$data_dir = "$logdir"."$data_dir";
$logfile = "$data_dir"."$logfile";

# �ʐݒ�t�@�C���捞
require $iniadd;

# �`�F�b�N�p���X�g�捞
require $checkpl;

#---------------------------------------------------------------------
# �Q�ƃy�[�W�����擾

$doc = '';

if ($ssi_mode) {

	if ($get_doc == 1) { $doc = $ENV{'REQUEST_URI'}; }
	elsif ($get_doc == 2) { $doc = $ENV{'DOCUMENT_URI'}; }
	elsif ($get_doc == 3) { $doc = $ENV{'DOCUMENT_NAME'}; }
	elsif ($get_doc == 4) { $doc = $ARGV[1]; }

} else {

	if ($get_doc == 1) { $doc = $httpref; }

}

#---------------------------------------------------------------------

# @killua
# @myhost

# $cookie_check
# $admin_check

# @killcall
# @killuri
# @deluri
# @repuria
# @repurib

# @repdoca
# @repdocb

# $host_check 

#---------------------------------------------------------------------
# UserAgent �����擾

$user_agent = $ENV{'HTTP_USER_AGENT'};
#$user_agent =~ tr/+/ /;
$user_agent =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
$user_agent =~ tr/\r\n//d;

# UserAgent �̃`�F�b�N
if ($user_agent) {
	foreach (@killua) {
		if ($_ eq '') { next; }
		$_ =~ s/\./\\./g;
		$_ =~ s/\?/\\?/g;
		$_ =~ s/\+/\\+/g;
		$_ =~ s/\*/\.\*/g;
		if ($user_agent =~ /$_/) { &putimage; }
	}
}

#---------------------------------------------------------------------
# �z�X�g�����擾

if ($get_remotehost == 1) {
	$addr = $ENV{'REMOTE_ADDR'};
	$host = gethostbyaddr(pack('C4', split(/\./, $addr)), 2);
} elsif ($get_remotehost == 2) {
	$addr = $ENV{'HTTP_X_FORWARDED_FOR'};
	$host = gethostbyaddr(pack('C4', split(/\./, $addr)), 2);
} else {
	$addr = $ENV{'REMOTE_ADDR'};
	$host = $ENV{'REMOTE_HOST'};
}

if ($host eq '') { $host = $addr; }

# ���O host �̃`�F�b�N
foreach (@myhost) {
	if ($_ eq '') { next; }
	$_ =~ s/\./\\./g;
	$_ =~ s/\*/\.\*/g;
	if ($host =~ /$_/) { &putimage; }
}

#---------------------------------------------------------------------
# cookie �̃`�F�b�N

unless ($ssi_mode) {

	if ($cookie_check || $admin_check) {
		&cookie_get;
		$co_check = time - $cookie_check * 60;
		if ($COOKIE{$cookie_name} > $co_check) { &putimage; }
		if ($admin_check) { if ($COOKIE{$cookie_admin} =~ /pass\!/) { &putimage; } }
	}

}

#---------------------------------------------------------------------
# �s���Ăяo���̃`�F�b�N

if ($httpref) {
	foreach (@killcall) {
		if ($_ eq '') { next; }
		$_ =~ s/\./\\./g;
		$_ =~ s/\?/\\?/g;
		$_ =~ s/\+/\\+/g;
		$_ =~ s/\*/\.\*/g;
		if ($httpref =~ /$_/) { &stop; }
	}
}

#---------------------------------------------------------------------
# �e�� URI �`�F�b�N

# �����N���� http:// �Ŏn�܂��Ă��Ȃ��ꍇ�͋󗓂ɂ���
#	if ($ref !~ /^http\:\/\//) { $ref = ''; }

# �����N�����V�t�gJIS�ϊ��i�����G���W������̃L�[���[�h�����j
	if ($ref && $decode) { require $jcode; &jcode'convert(*ref, 'sjis'); }

# ���O URI �̃`�F�b�N
if ($ref) {
	foreach (@killuri) {
		if ($_ eq '') { next; }
		$_ =~ s/\./\\./g;
		$_ =~ s/\?/\\?/g;
		$_ =~ s/\+/\\+/g;
		$_ =~ s/\*/\.\*/g;
		if ($ref =~ /$_/) { &putimage; }
	}
}

# �����N���擾���O�`�F�b�N
if ($ref) {
	foreach (@deluri) {
		if ($_ eq '') { next; }
		$_ =~ s/\./\\./g;
		$_ =~ s/\?/\\?/g;
		$_ =~ s/\+/\\+/g;
		$_ =~ s/\*/\.\*/g;
		if ($ref =~ /$_/) { $ref = ''; last; }
	}
}

$rc = 0;

# �����N����u�����i������v�j
unless ($ref eq '' || $ref =~ /google\..*?cache:/i) {
	foreach (@repuria) {
		if ($_ eq '') { next; }
		($key, $value) = split(/<>/, $_);
		$key =~ s/\./\\./g;
		$key =~ s/\?/\\?/g;
		$key =~ s/\+/\\+/g;
		$key =~ s/\*/\.\*/g;
		if ($ref =~ /$key/) { $ref = $value; $rc = 1; last; }
	}
}

# �����N����u�����i���S��v�j
unless ($ref eq '' || $rc == 1) {
	foreach (@repurib) {
		if ($_ eq '') { next; }
		($key, $value) = split(/<>/, $_);
		$key =~ s/\./\\./g;
		$key =~ s/\?/\\?/g;
		$key =~ s/\+/\\+/g;
		$key =~ s/\*/\.\*/g;
		if ($ref =~ /^$key$/) { $ref = $value; last; }
	}
}

#---------------------------------------------------------------------
# �Q�ƃy�[�W�`�F�b�N

if ($get_doc) {

	$dc = 0;

# �Q�ƃy�[�W��u�����i������v�j
	if ($doc) {
		foreach (@repdoca) {
			if ($_ eq '') { next; }
			($key, $value) = split(/<>/, $_);
			$key =~ s/\./\\./g;
			$key =~ s/\?/\\?/g;
			$key =~ s/\+/\\+/g;
			$key =~ s/\*/\.\*/g;
			if ($doc =~ /$key/) { $doc = $value; $dc = 1; last; }
		}
	}

# �Q�ƃy�[�W��u�����i���S��v�j
	unless ($doc eq '' || $dc == 1) {
			foreach (@repdocb) {
			if ($_ eq '') { next; }
			($key, $value) = split(/<>/, $_);
			$key =~ s/\./\\./g;
			$key =~ s/\?/\\?/g;
			$key =~ s/\+/\\+/g;
			$key =~ s/\*/\.\*/g;
			if ($doc =~ /^$key$/) { $doc = $value; last; }
		}
	}

}

#---------------------------------------------------------------------
# ���Ԃ��擾

	($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = gmtime(time + 60 * 60 * $gettime);

	$years = sprintf("%04d", $year + 1900);
	$mon = sprintf("%02d", $mon + 1);
	$day = sprintf("%02d", $mday);
	$hours = sprintf("%02d", $hour);
	$min = sprintf("%02d", $min);
	$sec = sprintf("%02d", $sec);

	$j_youbi = ('��','��','��','��','��','��','�y') [$wday];
#	$e_youbi = ('Sun','Mon','Tue','Wed','Thu','Fri','Sat') [$wday];

	$date = "$years/$mon/$day ($j_youbi) $hours:$min:$sec";
	$dates = "$years/$mon/$day ($j_youbi)";

#---------------------------------------------------------------------
# ���O�t�@�C���ɋL�^

	&write;

#---------------------------------------------------------------------
# �ŏI�o�͏���

# cookie ���o��
	if ($ssi_mode == 0 && $cookie_check) { &cookie_put; }

# �J�E���^�[���o��
	if ($counter_view) {
		if ($ssi_mode) { &text_view; } else { &png_view; }
	} else {
		if ($ssi_mode) { &stop; } else { &gif_view; }
	}

exit;

#=====================================================================
# ���O�L�^����

sub write {

	if ($lockkey) { &lock; }

# ���O�ǂݍ���
	open(IN, "$logfile") || &error("Open Error : $logfile");
	@lines = <IN>;
	close(IN);

# ���O�̃J�E���^�[���ƃz�X�g�����擾
	$log_write = 1;
	$count = @lines;

	if ($count < 1) { $n_no = $count_start; }
	else {
		($no,$da,$re,$us_a,$pi,$hos,$add,$do) = split(/ \, /, $lines[0]);
		$n_no = $no + 1;
		if ($host_check && $hos eq $host) {
			if ($get_doc == 0) { $n_no = $no; $log_write = 0; }
			elsif ($get_doc && $do eq $doc) { $n_no = $no; $log_write = 0; }
		}
	}

# ���O���X�V
	if ($log_write) {

		while ($max - 1 < @lines) { pop(@lines); }
		unshift(@lines, "$n_no , $date , $ref , $user_agent , $pixel , $host , $addr , $doc , \n");

		open(OUT, ">$logfile") || &error("Write Error : $logfile");
		print OUT @lines;
		close(OUT);

# �f�[�^���O���X�V

		$datafile = "$data_dir"."$years".'_'."$mon".'.dat';

		open(DATA, "$datafile");
		@datas = <DATA>;
		close(DATA);

		($data_date,$day_access) = split(/ \, /, $datas[0]);
		if ($data_date eq $dates) {
			$day_access = $day_access + 1;
			$data = qq{$data_date , $day_access , \n};
			shift(@datas);
		} else { $data = "$dates , 1 , \n"; }

		unshift(@datas, $data);

		open(OUT, ">$datafile");
		print OUT @datas;
		close(OUT);

# �f�[�^���O�t�@�C���̃p�[�~�b�V������ύX
		chmod (0606, "$datafile");

		}

	&unlock;

}

#=====================================================================
# �t�@�C�����b�N����

sub lock {

	local($retry) = 5;

# 3���ȏ�Â����b�N�͍폜����
	if (-e $lockfile) {
		($mtime) = (stat($lockfile))[9];
		if ($mtime < time - 180) { &unlock; }
	}

# symlink�֐������b�N
	if ($lockkey == 1) {
		while (!symlink(".", $lockfile)) {
			if (--$retry <= 0) { &error('Lock is busy'); }
			sleep(1);
		}
	}

# mkdir�֐������b�N
	elsif ($lockkey == 2) {
		while (!mkdir($lockfile, 0705)) {
			if (--$retry <= 0) { &error('Lock is busy'); }
			sleep(1);
		}
	}

	$lockflag = 1;

}

#---------------------------------------------------------------------

sub unlock {

	if ($lockkey == 1) { unlink($lockfile); }
	elsif ($lockkey == 2) { rmdir($lockfile); }

	$lockflag = 0;

}

#=====================================================================
# �G���[����

sub error {

	&unlock if ($lockflag);
	die "$_[0] : $!";

}

#=====================================================================
# cookie �o��

sub cookie_put {

	($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = gmtime(time + $cookie_del * 24 * 3600);

	$years = sprintf("%04d", $year + 1900);
	$day = sprintf("%02d", $mday);
	$hour = sprintf("%02d", $hour);
	$min  = sprintf("%02d", $min);
	$sec  = sprintf("%02d", $sec);
	$month = ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') [$mon];
	$youbi = ('Sun','Mon','Tue','Wed','Thu','Fri','Sat') [$wday];

	$date_gmt = "$youbi, $day\-$month\-$years $hour:$min:$sec GMT";
	$cookie_data = time;

	print "Set-Cookie: $cookie_name=$cookie_data; expires=$date_gmt\n";

}

#=====================================================================
# cookie �擾

sub cookie_get {

	$cookies = $ENV{'HTTP_COOKIE'};
	@pairs = split(/;/, $cookies);
	foreach $pair (@pairs) {
		($name, $value) = split(/=/, $pair, 2);
		$name =~ s/ //g;
		$value =~ s/"/&quot;/g;
		$value =~ s/</&lt;/g;
		$value =~ s/>/&gt;/g;
		$COOKIE{$name} = $value;
	}

}

#=====================================================================
# ���O�w��̉摜�o�͏���

sub putimage {

# cookie ���o��
	if ($ssi_mode == 0 && $cookie_check) { &cookie_put; }

	unless ($counter_view) {

		if ($ssi_mode) { &stop; } else { &gif_view; }

	} else {

		if ($lockkey) { &lock; }

# ���O�ǂݍ���
		open(IN, "$logfile") || &error("Open Error : $logfile");
		@lines = <IN>;
		close(IN);

# ���O�̃J�E���^�[�����擾
		$count = @lines;
		if ($count < 1) { $n_no = $count_start; }
		else {
			($no,$da,$re,$us_a,$pi,$hos,$add,$do) = split(/ \, /, $lines[0]);
			$n_no = $no;
		}

		&unlock;

# �J�E���^�[���o��
		if ($ssi_mode) { &text_view; } else { &png_view; }

	}

}

#=====================================================================
# ����GIF�\��

sub gif_view {

# ����GIF���`
	@dmy = ('47','49','46','38','39','61','02','00','02','00','80',
			'00','00','00','00','00','ff','ff','ff','21','f9','04',
			'01','00','00','01','00','2c','00','00','00','00','02',
			'00','02','00','00','02','02','8c','53','00','3b');

# ����GIF��\��
	print "Content-type: image/gif\n\n";
	foreach (@dmy) { $data = pack('C*', hex($_)); print $data; }

	exit;

}

#=====================================================================
# PNG�J�E���^�[�\��
# ���C�u�����Fpngren.pl [ SI-PNG�A���X�N���v�g Ver 1.0(2000/11/1) ] 
# ���쌠�ҁF�������� [ http://www.aurora.dti.ne.jp/~zom/Counter/ ]

sub png_view {

	$counter = sprintf($digit, $n_no);

	require $pngren_pl;

	@narabi = split(/ */, $counter);
	&pngren::PngRen($sipng, *narabi);

	exit;

}

#=====================================================================
# SSI�e�L�X�g�J�E���^�[�\��

sub text_view {

	$counter = sprintf($digit, $n_no);

	print "Content-type: text/plain\n\n";
	print $counter;

#	print "<!-- text -->";

	exit;

}


#=====================================================================
# ���쌠�\��

sub check {

	print "Content-type: text/plain\n\n";

print <<"_END_";
original�FKENT WEB - $ver
modified�Fat works - $acver
_END_

	exit;

}

#=====================================================================
# stop

sub stop {

	&unlock if ($lockflag);
	print "Content-Type: text/plain\n\n";
	exit;

}

#=====================================================================
