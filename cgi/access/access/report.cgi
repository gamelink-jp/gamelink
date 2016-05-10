#!/usr/bin/perl

#=====================================================================
# access cgi アクセス情報取得ファイル report.cgi (2002/05/19)
#---------------------------------------------------------------------
# Original Script
#	Access Report v2.21 (2002/02/04)
#	アクセス解析システム
#	Copyright(C) Kent Web 2002
#	webmaster@kent-web.com
#	http://www.kent-web.com/
#---------------------------------------------------------------------
# modified by himura
#	access cgi ver.2.12 (2002/05/19)
#	mail： himura@dolphin.plala.or.jp
#	site： http://air.vis.ne.jp/at-works/
#---------------------------------------------------------------------
$ver = 'Access Report v2.21';
$acver = 'access cgi ver.2.12';
#---------------------------------------------------------------------
# データ構造
#	ログ："NO , DATE , REF , USER_AGENT , PIXEL , HOST , ADDR , DOC , "
#	月別："DATES , ACCESS , "
#=====================================================================
# 環境設定

# 共通設定ファイル取込
require './common.ini';

# ロックファイル設定
$lock_dir = './lock/';
$lockfile = "$lock_dir".'report.lock';

#---------------------------------------------------------------------

# cookie 名称
$cookie_admin = 'access';

# cookie 消化日数
$cookie_del = '30';

#---------------------------------------------------------------------

# 日本語デコード除外（検索サービスの UTF-8 等）
@nodecode = (
	'search.msn.*results.asp?',
	'google.*search?*e=utf8',
	'google.*search?*e=utf-8',
	'lycos.co.jp?*ie=utf-8',
);

#=====================================================================
# 分岐

# QUERY_STRING のチェック
if ($ENV{'QUERY_STRING'} eq 'check') { &check; }

# REQUEST_METHOD のチェック
if ($ENV{'REQUEST_METHOD'} eq "POST") { &stop; }

#---------------------------------------------------------------------
# HTTP_REFERER と QUERY_STRING を取得してデコード

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
# ディレクトリ選択情報と解像度とリンク元を取得

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

# 解像度が“数字x数字”以外の場合は空欄にする
	if ($pixel =~ /(\d+)x(\d+)/) { $pixel = "$1x$2"; } else { $pixel = ''; }

}

#---------------------------------------------------------------------
# ディレクトリ設定取得

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

# 個別設定ファイル取込
require $iniadd;

# チェック用リスト取込
require $checkpl;

#---------------------------------------------------------------------
# 参照ページ情報を取得

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
# UserAgent 情報を取得

$user_agent = $ENV{'HTTP_USER_AGENT'};
#$user_agent =~ tr/+/ /;
$user_agent =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
$user_agent =~ tr/\r\n//d;

# UserAgent のチェック
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
# ホスト情報を取得

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

# 除外 host のチェック
foreach (@myhost) {
	if ($_ eq '') { next; }
	$_ =~ s/\./\\./g;
	$_ =~ s/\*/\.\*/g;
	if ($host =~ /$_/) { &putimage; }
}

#---------------------------------------------------------------------
# cookie のチェック

unless ($ssi_mode) {

	if ($cookie_check || $admin_check) {
		&cookie_get;
		$co_check = time - $cookie_check * 60;
		if ($COOKIE{$cookie_name} > $co_check) { &putimage; }
		if ($admin_check) { if ($COOKIE{$cookie_admin} =~ /pass\!/) { &putimage; } }
	}

}

#---------------------------------------------------------------------
# 不正呼び出しのチェック

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
# 各種 URI チェック

# リンク元が http:// で始まっていない場合は空欄にする
#	if ($ref !~ /^http\:\/\//) { $ref = ''; }

# リンク元をシフトJIS変換（検索エンジンからのキーワード処理）
	if ($ref && $decode) { require $jcode; &jcode'convert(*ref, 'sjis'); }

# 除外 URI のチェック
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

# リンク元取得除外チェック
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

# リンク元を置換え（部分一致）
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

# リンク元を置換え（完全一致）
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
# 参照ページチェック

if ($get_doc) {

	$dc = 0;

# 参照ページを置換え（部分一致）
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

# 参照ページを置換え（完全一致）
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
# 時間を取得

	($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = gmtime(time + 60 * 60 * $gettime);

	$years = sprintf("%04d", $year + 1900);
	$mon = sprintf("%02d", $mon + 1);
	$day = sprintf("%02d", $mday);
	$hours = sprintf("%02d", $hour);
	$min = sprintf("%02d", $min);
	$sec = sprintf("%02d", $sec);

	$j_youbi = ('日','月','火','水','木','金','土') [$wday];
#	$e_youbi = ('Sun','Mon','Tue','Wed','Thu','Fri','Sat') [$wday];

	$date = "$years/$mon/$day ($j_youbi) $hours:$min:$sec";
	$dates = "$years/$mon/$day ($j_youbi)";

#---------------------------------------------------------------------
# ログファイルに記録

	&write;

#---------------------------------------------------------------------
# 最終出力処理

# cookie を出力
	if ($ssi_mode == 0 && $cookie_check) { &cookie_put; }

# カウンターを出力
	if ($counter_view) {
		if ($ssi_mode) { &text_view; } else { &png_view; }
	} else {
		if ($ssi_mode) { &stop; } else { &gif_view; }
	}

exit;

#=====================================================================
# ログ記録処理

sub write {

	if ($lockkey) { &lock; }

# ログ読み込み
	open(IN, "$logfile") || &error("Open Error : $logfile");
	@lines = <IN>;
	close(IN);

# 直前のカウンター数とホスト情報を取得
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

# ログを更新
	if ($log_write) {

		while ($max - 1 < @lines) { pop(@lines); }
		unshift(@lines, "$n_no , $date , $ref , $user_agent , $pixel , $host , $addr , $doc , \n");

		open(OUT, ">$logfile") || &error("Write Error : $logfile");
		print OUT @lines;
		close(OUT);

# データログを更新

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

# データログファイルのパーミッションを変更
		chmod (0606, "$datafile");

		}

	&unlock;

}

#=====================================================================
# ファイルロック処理

sub lock {

	local($retry) = 5;

# 3分以上古いロックは削除する
	if (-e $lockfile) {
		($mtime) = (stat($lockfile))[9];
		if ($mtime < time - 180) { &unlock; }
	}

# symlink関数式ロック
	if ($lockkey == 1) {
		while (!symlink(".", $lockfile)) {
			if (--$retry <= 0) { &error('Lock is busy'); }
			sleep(1);
		}
	}

# mkdir関数式ロック
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
# エラー処理

sub error {

	&unlock if ($lockflag);
	die "$_[0] : $!";

}

#=====================================================================
# cookie 出力

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
# cookie 取得

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
# 除外指定の画像出力処理

sub putimage {

# cookie を出力
	if ($ssi_mode == 0 && $cookie_check) { &cookie_put; }

	unless ($counter_view) {

		if ($ssi_mode) { &stop; } else { &gif_view; }

	} else {

		if ($lockkey) { &lock; }

# ログ読み込み
		open(IN, "$logfile") || &error("Open Error : $logfile");
		@lines = <IN>;
		close(IN);

# 直前のカウンター数を取得
		$count = @lines;
		if ($count < 1) { $n_no = $count_start; }
		else {
			($no,$da,$re,$us_a,$pi,$hos,$add,$do) = split(/ \, /, $lines[0]);
			$n_no = $no;
		}

		&unlock;

# カウンターを出力
		if ($ssi_mode) { &text_view; } else { &png_view; }

	}

}

#=====================================================================
# 透過GIF表示

sub gif_view {

# 透過GIFを定義
	@dmy = ('47','49','46','38','39','61','02','00','02','00','80',
			'00','00','00','00','00','ff','ff','ff','21','f9','04',
			'01','00','00','01','00','2c','00','00','00','00','02',
			'00','02','00','00','02','02','8c','53','00','3b');

# 透過GIFを表示
	print "Content-type: image/gif\n\n";
	foreach (@dmy) { $data = pack('C*', hex($_)); print $data; }

	exit;

}

#=====================================================================
# PNGカウンター表示
# ライブラリ：pngren.pl [ SI-PNG連結スクリプト Ver 1.0(2000/11/1) ] 
# 著作権者：桜月さま [ http://www.aurora.dti.ne.jp/~zom/Counter/ ]

sub png_view {

	$counter = sprintf($digit, $n_no);

	require $pngren_pl;

	@narabi = split(/ */, $counter);
	&pngren::PngRen($sipng, *narabi);

	exit;

}

#=====================================================================
# SSIテキストカウンター表示

sub text_view {

	$counter = sprintf($digit, $n_no);

	print "Content-type: text/plain\n\n";
	print $counter;

#	print "<!-- text -->";

	exit;

}


#=====================================================================
# 著作権表示

sub check {

	print "Content-type: text/plain\n\n";

print <<"_END_";
original：KENT WEB - $ver
modified：at works - $acver
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
