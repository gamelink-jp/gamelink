#!/usr/bin/perl

#=====================================================================
# access cgi ��̓��X�g�\���t�@�C�� replist.cgi (2002/05/19)
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

# �Ǘ��҃p�X���[�h
$pass = 'yt112';

# �X�N���v�g
$cgi = './replist.cgi';

#---------------------------------------------------------------------

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

#=====================================================================
# ����

if ($ENV{'QUERY_STRING'} eq 'check') { &check; }

&decode;

if ($FORM{'pass'} ne $pass) { &password; }

#---------------------------------------------------------------------
# �f�B���N�g���ݒ�擾

unless ($FORM{'logdir'}) { $FORM{'logdir'} = $default_ini; }

foreach (@log_dir) {
	if ($_ eq '') { next; }
	($key, $value) = split(/<>/, $_);
	if ($FORM{'logdir'} eq $key) { $logdir = $value; last; }
}

$iniadd = "$logdir"."$iniadd";
$titlepl = "$logdir"."$titlepl";
$data_dir = "$logdir"."$data_dir";
$logfile = "$data_dir"."$logfile";

# �ʐݒ�t�@�C���捞
require $iniadd;

#---------------------------------------------------------------------

if ($FORM{'action'} eq 'delete') { &delete; }
elsif ($FORM{'action'} eq 'dellink') { &dellink; }
elsif ($FORM{'action'} eq 'convert') { &convert; }
elsif ($FORM{'data'} ne '') { &datamain; }
elsif ($FORM{'hour'} ne '') { &hourmain; }
elsif ($FORM{'list'} ne '') { &listmain; }
else { &logmain; }

exit;

#=====================================================================
# �t�H�[���f�[�^�ϊ�

sub decode {

	if ($ENV{'REQUEST_METHOD'} eq "POST") { read (STDIN, $post, $ENV{CONTENT_LENGTH}); }
	elsif ($ENV{'QUERY_STRING'}) { &stop; }

	@pairs = split(/&/, $post);
	foreach $pair (@pairs){
		($name, $value) = split(/=/, $pair);
		$value =~ tr/+/ /;
		$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
		$value =~ s/</&lt;/g;
		$value =~ s/>/&gt;/g;
		$value =~ tr/\r\n//d;
		if ($name eq 'no') { push(@DEL, $value); }
		elsif ($name eq 'link') { push(@DEL, $value); }
		else { $FORM{$name} = $value; }
	}

}

#=====================================================================
# �����擾����

sub time {

	($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = gmtime(time - $minus + 60 * 60 * $gettime);

	$years = sprintf("%04d", $year + 1900);
	$mon = sprintf("%02d", $mon + 1);
	$day = sprintf("%02d", $mday);
	$hour = sprintf("%02d", $hour);
	$min = sprintf("%02d", $min);
	$sec = sprintf("%02d", $sec);

	$j_youbi = ('��','��','��','��','��','��','�y') [$wday];
#	$e_youbi = ('Sun','Mon','Tue','Wed','Thu','Fri','Sat') [$wday];

#	$date = "$years/$mon/$day ($j_youbi) $hour:$min:$sec";
	$dates = "$years/$mon/$day ($j_youbi)";

}

#=====================================================================
# �A�N�Z�X���O���������iKENT WEB - Web Forum v3.x ����̈ڐA�j

sub logsearch {

	$FORM{'word'} =~ s/�@/ /g;
	@pairs = split(/\s+/, $FORM{'word'});

	if ($lockkey) { &lock; }

	open(IN, "$logfile") || &error("Open Error : $logfile");
	while (<IN>) {
		$flag = 0;
		foreach $pair (@pairs) {
			if (index ($_, $pair) >= 0) { $flag = 1; if ($FORM{'mode'} eq 'or') { last; } }
			else { if ($FORM{'mode'} eq 'and') { $flag = 0; last; } }
		}
		if ($flag) { push (@new, $_); }
	}
	close(IN);

	&unlock;

}

#=====================================================================
# �z�X�g��񖔂� IP�A�h���X�̃}�X�N����

sub host_data {

	if ($host =~ /(.*)\.(\d+)$/) { $host = qq{$1.*}; }
	elsif ($host =~ /(.*)\.(.*)\.(.*)\.(.*)$/) { $host = qq{*.$2.$3.$4}; }
	elsif ($host =~ /(.*)\.(.*)\.(.*)$/) { $host = qq{*.$2.$3}; }

	if ($addr =~ /(.*)\.(\d+)$/) { $addr = qq{$1.*}; }

}

#=====================================================================
# �ʏ�񃁃C������

sub logmain {

	&cookie_put;
	&view_data;

	if ($FORM{'word'}) { &logsearch; }	# �A�N�Z�X���O����
	if ($rt_view) { require $titlepl; }	# �����N���\���u�����X�g�捞
	require $searchpl;	# �����T�[�r�X��̓��C�u�����捞

	$count = 0;

	if ($FORM{'word'}) { foreach $line (@new) { &logline; } }
	else {
		if ($lockkey) { &lock; }

		open(IN, "$logfile") || &error("Open Error : $logfile");
		while (<IN>) { $line = $_; &logline; }
		close(IN);

		&unlock;
	}

	&cookie_get;

	$list_start = '<!-- list_start -->';
	$data_end = '<!-- data_end -->';

	open(MAIN, "$main_html");
	@mainhtml = <MAIN>;
	close(MAIN);

	print "Content-Type: text/html\n\n";
	foreach $main (@mainhtml) {
		if ($main =~ /<!-- log_html -->/i) { &log; }
		elsif ($main =~ /<!-- link_html -->/i) { &link; }
		elsif ($main =~ /<!-- keyword_html -->/i) { &keyword; }
		elsif ($main =~ /<!-- document_html -->/i) { &document; }
		if ($main =~ s/$list_start//io) { $main_del = 1; }
		if ($main =~ s/$data_end//io) { $main_del = 0; }
		if ($main_del) { next; }
		if ($main =~ /<!-- copy_html -->/i) { &copy; }
		&htmldata;
		print $main;
	}

	exit;

}

#---------------------------------------------------------------------
# �����T�[�r�X�����擾

sub key_data {

	&search_service;

	$refq =~ s/�@/ /g;
	$refq =~ s/^\s+//;
	$refq =~ s/\s+$//;
	$refq =~ s/\s+/ /g;

	if ($refq) {
		if ($keys_mode) {
			@keywords = split(/\s+/, $refq);
			foreach $keyword (@keywords) { $REFK{($keyword)[0]}++; $k++; }
		} else { $REFK{($refq)[0]}++; $k++; }
	}

	if ($refs) {
		while (($key, $value) = each %searchsite) {
			if ($key eq '') { next; }
			elsif ($refs eq $key) { $ref = $value; }
		}
	}

}

#---------------------------------------------------------------------
# �A�N�Z�X���O�f�[�^���擾

sub logline {

	$count++;

	$line =~ tr/\n//d;
	if ($count <= $log_view) { push @lines, $line; }
	($no,$date,$ref,$user_agent,$pixel,$host,$addr,$doc) = split(/ \, /, $line);

	if ($count == 1) { $counter = $no; $new_date = $date; }
	$old_date = $date;

	if ($ref eq '' || $ref eq 'bookmark') { $ref = 'none'; $REF{($ref)[0]}++; $r++; }
	else {
		if ($se_view) { &key_data; $REF{($ref)[0]}++; $r++; }
		else { $REF{($ref)[0]}++; $r++; &key_data; }
	}

	unless ($doc) { $doc = 'none'; }
	$DOC{($doc)[0]}++; $d++;

}

#=====================================================================
# �ʏ��

sub log {

	if ($ua_view) { require $agentpl; $ua_others = $os_others = 0; }

	foreach $lines (@lines) {

		($no,$date,$ref,$user_agent,$pixel,$host,$addr,$doc) = split(/ \, /, $lines);

		if ($ref eq '' || $ref eq 'bookmark') { $uri = $ref = '-'; }
		else { $r_length = $lref_length; &reftitle; }

		unless ($doc) { $doc = 'none'; }

		if ($user_agent) {
			if ($ua_view) { &user_agent; $logua = $osa; }
			else { $logua = $user_agent; }
		} else { $logua = $user_agent = '-'; }

		$user_agent =~ s/&/&amp;/g;
		$user_agent =~ s/"/&quot;/g;
		$user_agent =~ s/</&lt;/g;
		$user_agent =~ s/>/&gt;/g;

		$logua =~ s/&/&amp;/g;
		$logua =~ s/"/&quot;/g;
		$logua =~ s/</&lt;/g;
		$logua =~ s/>/&gt;/g;

		unless ($pixel) { $pixel = '-'; }

		if ($sample_view) { &host_data; }

		if ($do_view) { $uri_data = qq{$uri<br /><span class="document">�� $doc</span>}; }
		else { $uri_data = $uri; }

		if ($ip_view) {
			if ($addr eq $host|$addr eq "\n"|$addr eq '') { $host_data = $host; }
			else { $host_data = qq{$host <span class="addr">[$addr]</span>}; }
		} else { $host_data = $host; }

print <<"_END_";

<tr class="listtable">
<th align="right" valign="top" abbr="number">$no</th>
<td>$date</td>
<td>$uri_data</td>
<td title="$user_agent">$logua</td>
<td>$pixel</td>
<td title="$addr">$host_data</td>
<td align="center"><input type="checkbox" name="no" value="$no" title="$no" /></td>
</tr>

_END_

	}

}

#---------------------------------------------------------------------
# �����N���\���̒u������

sub reftitle {

# �����񒷂̒���

	if ($r_length && length($ref) > $r_length) {
		$reflengths = $r_length - 4;
		$uri = substr($ref, 0, $reflengths) . "....";
	} else { $uri = $ref; }

	$reptitle = 0;

	if ($rt_view) {
		while (($key, $value) = each %rtitle) {
			if ($key eq '') { next; }
			elsif ($ref eq $key) { $uri = $value; $reptitle = 1; }
		}
		unless ($reptitle) {
			while (($key, $value) = each %searchtitle) {
				if ($key eq '') { next; }
				elsif ($ref eq $key) { $uri = $value; $reptitle = 1; }
			}
		}
	}

	$ref =~ s/&/&amp;/g;
	$ref =~ s/"/&quot;/g;
	$ref =~ s/</&lt;/g;
	$ref =~ s/>/&gt;/g;

	$uri =~ s/&/&amp;/g;
	$uri =~ s/"/&quot;/g;
	$uri =~ s/</&lt;/g;
	$uri =~ s/>/&gt;/g;

	$jref = $ref;
	if ($jp_view) {
		$jref =~ s/^http:\/\/(.*?)/$jump_uri\/$1/io;
		$jref =~ s/(ime.nu\/)+/$1/ig;
	}

	if ($ref =~ /^http:\/\//) {
		if ($reptitle) { $uri = qq{<a href="$jref" title="$ref" class="reptitle">$uri</a>}; }
		else { $uri = qq{<a href="$jref" title="$ref">$uri</a>}; }
	}

}

#---------------------------------------------------------------------
# �����N�����

sub link {

	foreach (sort { $REF{$b} <=> $REF{$a} } keys %REF) {

		if ($REF{$_} < $ref_view) { last; }

		$per = int(($REF{$_} * 1000 / $r) + 0.5) / 10;
		$per = sprintf("%.1f", $per);
		$wid = int($per * $ref_width);
		if ($width < 1) { $width = 1; }

		if ($_ eq 'none') { $uri = $_; $ref = ''; }
		else { $ref = $_; $r_length = $ref_length; &reftitle; }

print <<"_END_";

<tr class="listtable">
<th align="right" abbr="count">$REF{$_}</th>
<td>$uri</td>
<td title="$ref"><img src="$graph1" width="$wid" height="10" alt="" /> $per%</td>
<td align="center" title="$ref"><input type="checkbox" name="link" value="$ref" /></td>
</tr>

_END_

	}

}

#---------------------------------------------------------------------
# �����L�[���[�h���

sub keyword {

	foreach (sort { $REFK{$b} <=> $REFK{$a} } keys %REFK) {

		if ($REFK{$_} < $key_view) { last; }

		$per = int(($REFK{$_} * 1000 / $k) + 0.5) / 10;
		$per = sprintf("%.1f", $per);
		$wid = int($per * $key_width);
		if ($width < 1) { $width = 1; }

		$refk = $_;

		$refk =~ s/&/&amp;/g;
		$refk =~ s/"/&quot;/g;
		$refk =~ s/</&lt;/g;
		$refk =~ s/>/&gt;/g;

		$search_uri =~ s/&/&amp;/g;
		$search_uri =~ s/"/&quot;/g;
		$search_uri =~ s/</&lt;/g;
		$search_uri =~ s/>/&gt;/g;

# URL�G���R�[�h
# $refk =~ s/(\W)/'%'.unpack("H2", $1)/ego;

		$uri = qq{<a href="$search_uri$refk" title="$search_uri$refk">$refk</a>};

print <<"_END_";

<tr class="listtable">
<th align="right" abbr="count">$REFK{$_}</th>
<td>$uri</td>
<td title="$refk"><img src="$graph1" width="$wid" height="10" alt="" /> $per%</td>
</tr>

_END_

	}

}

#---------------------------------------------------------------------
# �����L�[���[�h���

sub document {

	foreach (sort { $DOC{$b} <=> $DOC{$a} } keys %DOC) {

		if ($DOC{$_} < $doc_view) { last; }

		$per = int(($DOC{$_} * 1000 / $d) + 0.5) / 10;
		$per = sprintf("%.1f", $per);
		$wid = int($per * $doc_width);
		if ($width < 1) { $width = 1; }

		$doc = $_;

		$doc =~ s/&/&amp;/g;
		$doc =~ s/"/&quot;/g;
		$doc =~ s/</&lt;/g;
		$doc =~ s/>/&gt;/g;

print <<"_END_";

<tr class="listtable">
<th align="right" abbr="count">$DOC{$_}</th>
<td>$doc</td>
<td title="$doc"><img src="$graph1" width="$wid" height="10" alt="" /> $per%</td>
</tr>

_END_

	}

}

#=====================================================================
# ��̓��X�g�\�����C������

sub listmain {

	require $agentpl;	# UserAgent��̓��C�u�����捞

	&view_data;

	if ($FORM{'word'}) { &logsearch; }	# �A�N�Z�X���O����

	$count = 0;

	if ($FORM{'word'}) { foreach $line (@new) { &listline; } }
	else {
		if ($lockkey) { &lock; }

		open(IN, "$logfile") || &error("Open Error : $logfile");
		while (<IN>) { $line = $_; &listline; }
		close(IN);

		&unlock;
	}

	&cookie_get;

	$main_start = '<!-- main_start -->';
	$main_end = '<!-- main_end -->';
	$time_start = '<!-- time_start -->';
	$data_end = '<!-- data_end -->';

	open(MAIN, "$main_html");
	@mainhtml = <MAIN>;
	close(MAIN);

	print "Content-Type: text/html\n\n";
	foreach $main (@mainhtml) {
		if ($main =~ s/$main_start//io) { $main_del = 1; }
		if ($main =~ s/$main_end//io) { $main_del = 0; }
		if ($main_del) { next; }
		elsif ($main =~ /<!-- pixel_html -->/i) { &pixel; }
		elsif ($main =~ /<!-- agent_html -->/i) { &agent; }
		elsif ($main =~ /<!-- os_html -->/i) { &os; }
		elsif ($main =~ /<!-- host_html -->/i) { &host; }
		if ($main =~ s/$time_start//io) { $data_del = 1; }
		if ($main =~ s/$data_end//io) { $data_del = 0; }
		if ($data_del) { next; }
		if ($main =~ /<!-- copy_html -->/i) { &copy; }
		&htmldata;
		print $main;
	}

	exit;

}

#---------------------------------------------------------------------
# �A�N�Z�X���O�f�[�^���擾

sub listline {

	$count++;

	$line =~ tr/\n//d;
	($no,$date,$ref,$user_agent,$pixel,$host,$addr,$doc) = split(/ \, /, $line);

	if ($count == 1) { $counter = $no; $new_date = $date; }
	$old_date = $date;

	unless ($pixel) { $pixel = '[none]'; }

	if ($user_agent) {
		if ($ua_count == 1) { $ua_view = 0; &user_agent; $agent = $osa; }
		elsif ($ua_count == 2) { $ua_view = 1; &user_agent; }
		elsif ($ua_count == 3) { $ua_view = 1; &user_agent; $agent = $osa; }
		elsif ($ua_count == 4) { &user_agent; $agent = $user_agent;  }
		else { $ua_view = 0; &user_agent; }
	} else { $agent = $os = '[none]'; }

	if ($ip_count) { $host = $addr; }
	&host_data;

	if ($pixel) { $PIXEL{($pixel)[0]}++; $p++; }
	if ($agent) { $AGENT{($agent)[0]}++; $a++; }
	if ($os) { $OS{($os)[0]}++; $o++; }
	if ($host) { $HOST{($host)[0]}++; $h++; }

}

#=====================================================================
# �𑜓x���

sub pixel {

	foreach (sort { $PIXEL{$b} <=> $PIXEL{$a} } keys %PIXEL) {
		if ($PIXEL{$_} < $pixel_view) { last; }
		$COUNT = $PIXEL{$_}; $all = $p;
		&graph;
	}

}

#---------------------------------------------------------------------
# �u���E�U���

sub agent {

	foreach (sort { $AGENT{$b} <=> $AGENT{$a} } keys %AGENT) {
		if ($AGENT{$_} < $agent_view) { last; }
		$COUNT = $AGENT{$_}; $all = $a;
		s/&/&amp;/g;
		s/"/&quot;/g;
		s/</&lt;/g;
		s/>/&gt;/g;
		&graph;
	}

}

#---------------------------------------------------------------------
# OS���

sub os {

	foreach (sort { $OS{$b} <=> $OS{$a} } keys %OS) {
		if ($OS{$_} < $os_view) { last; }
		$COUNT = $OS{$_}; $all = $o;
		s/&/&amp;/g;
		s/"/&quot;/g;
		s/</&lt;/g;
		s/>/&gt;/g;
		&graph;
	}

}

#---------------------------------------------------------------------
# �z�X�g���

sub host {

	foreach (sort { $HOST{$b} <=> $HOST{$a} } keys %HOST) {
		if ($HOST{$_} < $host_view) { last; }
		$COUNT = $HOST{$_}; $all = $h;
		&graph;
	}

}

#---------------------------------------------------------------------
# �����O���t�\������

sub graph {

	$per = int(($COUNT * 1000 / $all) + 0.5) / 10;
	$per = sprintf("%.1f", $per);
	$wid = int($per * $gra_width);
	if ($width < 1) { $width = 1; }

	$graph_view = qq{<img src="$graph1" width="$wid" height="10" alt="" />};
	unless ($COUNT) { $graph_view = ""; }

print <<"_END_";

<tr class="listtable">
<th align="right" abbr="count">$COUNT</th>
<td class="item">$_</td>
<td>$graph_view $per%</td>
</tr>

_END_

}

#=====================================================================
# ���ԑѕʕ\�����C������

sub hourmain {

	$minus = 0; &time; $today = $dates;
	$minus = 86400; &time; $yesterday = $dates;
	$minus = 172800; &time; $dbyesterday = $dates;

	if ($FORM{'word'}) { &logsearch; }	# �A�N�Z�X���O����

	$count = 0;

	if ($FORM{'word'}) { foreach $line (@new) { &hourline; } }
	else {
		if ($lockkey) { &lock; }

		open(IN, "$logfile") || &error("Open Error : $logfile");
		while (<IN>) { $line = $_; &hourline; }
		close(IN);

		&unlock;
	}

	&cookie_get;

	$main_start = '<!-- main_start -->';
	$list_end = '<!-- list_end -->';
	$data_start = '<!-- data_start -->';
	$data_end = '<!-- data_end -->';

	open(MAIN, "$main_html");
	@mainhtml = <MAIN>;
	close(MAIN);

	print "Content-Type: text/html\n\n";
	foreach $main (@mainhtml) {
		if ($main =~ s/$main_start//io) { $main_del = 1; }
		if ($main =~ s/$list_end//io) { $main_del = 0; }
		if ($main_del) { next; }
		if ($main =~ /<!-- today_html -->/i) { $TI = $today; $hc = $tod; &hours; }
		elsif ($main =~ /<!-- yesterday_html -->/i) { $TI = $yesterday; $hc = $yed; &hours; }
		elsif ($main =~ /<!-- dbyday_html -->/i) { $TI = $dbyesterday; $hc = $dbd; &hours; }
		elsif ($main =~ /<!-- mon_html -->/i) { $TI = '��'; $hc = $mod; &hours; }
		elsif ($main =~ /<!-- tue_html -->/i) { $TI = '��'; $hc = $tud; &hours; }
		elsif ($main =~ /<!-- wed_html -->/i) { $TI = '��'; $hc = $wed; &hours; }
		elsif ($main =~ /<!-- thu_html -->/i) { $TI = '��'; $hc = $thd; &hours; }
		elsif ($main =~ /<!-- fri_html -->/i) { $TI = '��'; $hc = $frd; &hours; }
		elsif ($main =~ /<!-- sat_html -->/i) { $TI = '�y'; $hc = $sad; &hours;; }
		elsif ($main =~ /<!-- sun_html -->/i) { $TI = '��'; $hc = $sud; &hours; }
		elsif ($main =~ /<!-- time_html -->/i) { $TI = 'all'; $hc = $t; &hours; }
		elsif ($main =~ /<!-- wday_html -->/i) { &wday; }
		if ($main =~ s/$data_start//io) { $data_del = 1; }
		if ($main =~ s/$data_end//io) { $data_del = 0; }
		if ($data_del) { next; }
		if ($main =~ /<!-- copy_html -->/i) { &copy; }
		&htmldata;
		print $main;
	}

	exit;

}

#---------------------------------------------------------------------
# �A�N�Z�X���O�f�[�^���擾

sub hourline {

	$count++;

	$line =~ tr/\n//d;
	($no,$date,$ref,$user_agent,$pixel,$host,$addr,$doc) = split(/ \, /, $line);

	if ($count == 1) { $counter = $no; $new_date = $date; }
	$old_date = $date;

	&date_data;

}

#---------------------------------------------------------------------
# ���������擾

sub date_data {

	$date =~ /(\d\d\d\d\/\d\d\/\d\d \((.*?)\)) (\d\d):(\d\d:\d\d)/i;
	$days = $1; 
	$wdays = $2;
	$hours = int($3);

	if ($days eq $today) { $TODAY{($hours)[0]}++; $tod++; }
	if ($days eq $yesterday) { $YESTERDAY{($hours)[0]}++; $yed++; }
	if ($days eq $dbyesterday) { $DBYESTERDAY{($hours)[0]}++; $dbd++; }

	if ($wdays eq '��') { $MON{($hours)[0]}++; $mod++; }
	elsif ($wdays eq '��') { $TUE{($hours)[0]}++; $tud++; }
	elsif ($wdays eq '��') { $WED{($hours)[0]}++; $wed++; }
	elsif ($wdays eq '��') { $THU{($hours)[0]}++; $thd++; }
	elsif ($wdays eq '��') { $FRI{($hours)[0]}++; $frd++; }
	elsif ($wdays eq '�y') { $SAT{($hours)[0]}++; $sad++; }
	elsif ($wdays eq '��') { $SUN{($hours)[0]}++; $sud++; }

	$HOUR{($hours)[0]}++; $t++;
	$WDAY{($wdays)[0]}++; $w++;

}

#=====================================================================
# ���ԑѕʏW�v����

sub hours {

	$hc = int($hc);

	print qq{<tr class="listtable"><th align="right" abbr="count">$hc</th><th abbr="item" class="item">$TI</th>\n};

	foreach (0 .. 23) {

		if ($TI eq $today) { $TIME = $TODAY{$_}; }
		elsif ($TI eq $yesterday) { $TIME = $YESTERDAY{$_}; }
		elsif ($TI eq $dbyesterday) { $TIME = $DBYESTERDAY{$_}; }
		elsif ($TI eq '��') { $TIME = $MON{$_}; }
		elsif ($TI eq '��') { $TIME = $TUE{$_}; }
		elsif ($TI eq '��') { $TIME = $WED{$_}; }
		elsif ($TI eq '��') { $TIME = $THU{$_}; }
		elsif ($TI eq '��') { $TIME = $FRI{$_}; }
		elsif ($TI eq '�y') { $TIME = $SAT{$_}; }
		elsif ($TI eq '��') { $TIME = $SUN{$_}; }
		elsif ($TI eq 'all') { $TIME = $HOUR{$_}; }

		$TIME = int($TIME);

		if ($TI eq $today || $TI eq $yesterday || $TI eq $dbyesterday ||$TI eq 'all') {
				print qq{<td valign="bottom" align="center" class="hourcount">$TIME<br />};
				if ($TIME) { print qq{<img src="$graph2" width="6" height="$TIME" alt="" />}; }
		} else {
				print qq{<td valign="bottom" align="right" class="hourcount">$TIME<br />};
		}
		print "</td>\n";

	}

	print qq{</tr>\n};

}

#---------------------------------------------------------------------
# �j���ʏW�v

sub wday {

	if ($w) {
		$_ = '��'; &wdays;
		$_ = '��'; &wdays;
		$_ = '��'; &wdays;
		$_ = '��'; &wdays;
		$_ = '��'; &wdays;
		$_ = '�y'; &wdays;
		$_ = '��'; &wdays;
	}

}

sub wdays {

	$COUNT = int($WDAY{$_}); $all = $w; &graph;

}

#=====================================================================
# �f�[�^���O���\�����C������

sub datamain {

	if ($FORM{'years'} && $FORM{'mon'}) {

		$years = $FORM{'years'};
		$mon = sprintf("%02d", $FORM{'mon'});

	} else { $minus = 0; &time; }

	&cookie_get;

	$main_start = '<!-- main_start -->';
	$time_end = '<!-- time_end -->';

	open(MAIN, "$main_html");
	@mainhtml = <MAIN>;
	close(MAIN);

	print "Content-Type: text/html\n\n";
	foreach $main (@mainhtml) {
		if ($main =~ s/$main_start//io) { $main_del = 1; }
		if ($main =~ s/$time_end//io) { $main_del = 0; }
		if ($main_del) { next; }
		if ($main =~ /<!-- days_html -->/i) { &days; }
		elsif ($main =~ /<!-- month_html -->/i) { &month; }
		elsif ($main =~ /<!-- copy_html -->/i) { &copy; }
		&htmldata;
		print $main;
	}

	exit;

}

#=====================================================================
# ���ʏW�v����

sub days {

	$d = 0;
	$datafile = "$data_dir"."$years".'_'."$mon".'.dat';

	if ($lockkey) { &lock; }

	open(DATA, "$datafile");
	while (<DATA>) {
		($data_date,$day_access) = split(/ \, /, $_);
		$DAYS{($data_date)[0]} = $day_access;
		$d = $d + $day_access;
	}
	close(DATA);

	&unlock;

	foreach (sort { $b cmp $a } keys %DAYS) {
		$COUNT = int($DAYS{$_}); $all = $d; &graph;
	}

print <<"_END_";

<tr class="listtable">
<th align="right" abbr="count">$d</th>
<th abbr="total">���v</th>
<th abbr="graph">�O���t</th>
</tr>

_END_

}

#---------------------------------------------------------------------
# ���ʏW�v����

sub month {

	$total = 0;
	$data_dir =~ s/\/$//;

	if ($datalist) {
		open(DLIST, "$data_dir/datalist.dat");
		@datas = <DLIST>;
		close(DLIST);
	} else { @datas = glob("$data_dir/*.dat"); }

	foreach $datafile (@datas) {

		$datafile =~ s/((\d\d\d\d)_(\d\d)\.dat)/$1/;
		$datafile = $1;
		$month = "$2".'�N'."$3".'��'; 
		$m = 0;

		open(DATA, "$data_dir/$datafile");
		while (<DATA>) {
			($data_date,$day_access) = split(/ \, /, $_);
			$m = $m + $day_access;
		}
		close(DATA);

		$MONTH{($month)[0]} = $m;
		$total = $total + $m;

	}

	foreach (sort { $b cmp $a } keys %MONTH) {
		$COUNT = int($MONTH{$_}); $all = $total; &graph;
	}

print <<"_END_";

<tr class="listtable">
<th align="right" abbr="count">$total</th>
<th abbr="total">���v</th>
<th abbr="graph">�O���t</th>
</tr>

_END_

}

#=====================================================================
# �ʃf�[�^�폜����

sub delete {

	if ($sample_view) { &error("�{�����[�h�ł�"); }
	unless (@DEL) { &logmain; }

	&cookie_put;

	if ($lockkey) { &lock; }

	if (!open(IN, "$logfile")) { &error("Open Error : $logfile"); }
	while ($line = <IN>) {
		($no,$date,$ref,$user_agent,$pixel,$host,$addr,$doc) = split(/ \, /, $line);
		$match = 0;
		foreach $del (@DEL) { if ($no == $del) { $match = 1; } }
		if ($match == 0) { push (@DELETE, $line); }
	}
	close(IN);

	if (!open(OUT, ">$logfile")) { &error("Write Error : $logfile"); }
	print OUT @DELETE;
	close(OUT);

	&unlock;

	&logmain;

}

#=====================================================================
# �����N���f�[�^�폜����

sub dellink {

	if ($sample_view) { &error("�{�����[�h�ł�"); }
	unless (@DEL) { &logmain; }

	&cookie_put;

# �����T�[�r�X��̓��C�u�����捞
	if ($FORM{'sepl'} eq 'on') { require $searchpl; $se_del = 1; }

	if ($lockkey) { &lock; }

	if (!open(IN, "$logfile")) { &error("Open Error : $logfile"); }
	while ($line = <IN>) {
		$line =~ tr/\n//d;
		($no,$date,$ref,$user_agent,$pixel,$host,$addr,$doc) = split(/ \, /, $line);

		if ($ref) {
			foreach $del (@DEL) {

				if ($se_del) {
					&search_service;
					if ($refs) {
						while (($key, $value) = each %searchsite) {
							if ($key eq '') { next; }
						elsif ($refs eq $key) { $refs = $value; }
						}
					}
				}
				if ($ref eq $del || $refs eq $del) { $ref = ''; }

			}
		}

		$line = "$no , $date , $ref , $user_agent , $pixel , $host , $addr , $doc , \n";
		push (@DELETE, $line);
	}
	close(IN);

	if (!open(OUT, ">$logfile")) { &error("Write Error : $logfile"); }
	print OUT @DELETE;
	close(OUT);

	&unlock;

	&logmain;

}

#=====================================================================
# �����N���f�[�^��������

sub convert {

	if ($sample_view) { &error("�{�����[�h�ł�"); }
	unless ($FORM{'before'}) { &logmain; }

	&cookie_put;

	$before = $FORM{'before'};
	$after = $FORM{'after'};

# �����T�[�r�X��̓��C�u�����捞�y�у`�F�b�N
	if ($FORM{'sepl'} eq 'on') {
		require $searchpl;
		while (($value, $key) = each %searchsite) {
				if ($key eq '') { next; }
				$key =~ s/\?/\\?/g;
				$key =~ s/\+/\\+/g;
				$key =~ s/\[/\\[/g;
				$key =~ s/\]/\\]/g;
				if ($before =~ /$key/g) { &error("�����N�������T�[�r�X���\\�����[�h�̉������K�v�ł�"); }
		}
	}

	$before =~ s/\?/\\?/g;
	$before =~ s/\+/\\+/g;
	$before =~ s/\[/\\[/g;
	$before =~ s/\]/\\]/g;

	if ($lockkey) { &lock; }

	if (!open(IN, "$logfile")) { &error("Open Error : $logfile"); }
	while ($line = <IN>) {
		$line =~ tr/\n//d;
		($no,$date,$ref,$user_agent,$pixel,$host,$addr,$doc) = split(/ \, /, $line);
		if ($ref) { $ref =~ s/$before/$after/g; }
		$line = "$no , $date , $ref , $user_agent , $pixel , $host , $addr , $doc , \n";
		push (@DATA, $line);
	}
	close(IN);

	if (!open(OUT, ">$logfile")) { &error("Write Error : $logfile"); }
	print OUT @DATA;
	close(OUT);

	&unlock;

	&logmain;

}

#=====================================================================
# �t�@�C�����b�N����

# ���b�N����
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
# �N�b�L�[�o��

sub cookie_put {

	($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = gmtime(time + $cookie_del * 24 * 3600);

	$years = sprintf("%04d", $year + 1900);
	$emon = $mon;
	$mon = sprintf("%02d", $mon + 1);
	$day = sprintf("%02d", $mday);
	$hour = sprintf("%02d", $hour);
	$min  = sprintf("%02d", $min);
	$sec  = sprintf("%02d", $sec);
	$month = ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') [$emon];
	$youbi = ('Sun','Mon','Tue','Wed','Thu','Fri','Sat') [$wday];

	$date_gmt = "$youbi, $day\-$month\-$years $hour:$min:$sec GMT";
	$cookie_data = "pass\!$FORM{'pass'}";

	print "Set-Cookie: $cookie_admin=$cookie_data; expires=$date_gmt\n";

}

#=====================================================================
# �N�b�L�[�擾

sub cookie_get {

	$cookies = $ENV{'HTTP_COOKIE'};
	@pairs = split(/;/, $cookies);
	foreach $pair (@pairs) {
		($name, $value) = split(/=/, $pair, 2);
		$name =~ s/ //g;
		$value =~ s/"/&quot;/g;
		$value =~ s/</&lt;/g;
		$value =~ s/>/&gt;/g;
		$get{$name} = $value;
	}

	($name, $value) = split(/\!/, $get{$cookie_admin}, 2);
	$COOKIE{$name} = $value;

}

#=====================================================================
# �\�������擾

sub view_data {

	if ($FORM{'log'}) { $log_view = $FORM{'log'}; }
	if ($FORM{'ref'}) { $ref_view = $FORM{'ref'}; }
	if ($FORM{'key'}) { $key_view = $FORM{'key'}; }
	if ($FORM{'doc'}) { $doc_view = $FORM{'doc'}; }
	if ($FORM{'pixel'}) { $pixel_view = $FORM{'pixel'}; }
	if ($FORM{'agent'}) { $agent_view = $FORM{'agent'}; }
	if ($FORM{'os'}) { $os_view = $FORM{'os'}; }
	if ($FORM{'host'}) { $host_view = $FORM{'host'}; }

	if ($FORM{'do'}) { $do_view = 1; }
	else { if ($FORM{'mode'}) { $do_view = 0; } }

	if ($FORM{'ua'}) { $ua_view = 1; }
	else { if ($FORM{'mode'}) { $ua_view = 0; } }

	if ($FORM{'ip'}) { $ip_view = 1; }
	else { if ($FORM{'mode'}) { $ip_view = 0; } }

	if ($FORM{'rt'}) { $rt_view = 1; }
	else { if ($FORM{'mode'}) { $rt_view = 0; } }

	if ($FORM{'jp'}) { $jp_view = 1; }
	else { if ($FORM{'mode'}) { $jp_view = 0; } }

	if ($FORM{'se'}) { $se_view = 1; }
	else { if ($FORM{'mode'}) { $se_view = 0; } }

	if ($FORM{'keys'}) { $keys_mode = 1; }
	else { if ($FORM{'mode'}) { $keys_mode = 0; } }

	if ($FORM{'uao'}) { $ua_others = 1; }
	else { if ($FORM{'agent'}) { $ua_others = 0; } }

	if ($FORM{'uac'}) { $ua_count = $FORM{'uac'}; }
	else { if ($FORM{'agent'}) { $ua_count = 0; } }

	if ($FORM{'oso'}) { $os_others = 1; }
	else { if ($FORM{'agent'}) { $os_others = 0; } }

	if ($FORM{'ipc'}) { $ip_count = 1; }
	else { if ($FORM{'agent'}) { $ip_count = 0; } }

}

#=====================================================================
# HTML�f�[�^�ϊ�

sub htmldata {

	$main =~ s/href="main.css" media="/href="$css_dir\/main.css" media="/oi;
	$main =~ s/logdir_data/$FORM{'logdir'}/gi;

	$main =~ s/head_data/$title/gi;
	$main =~ s/title_data/$title/gi;
	$main =~ s/site_data/$site/gi;
	$main =~ s/return_data/$return/gi;

	$main =~ s/counter_data/$counter/gi;
	$main =~ s/count_data/$count/gi;
	$main =~ s/old_data/$old_date/gi;
	$main =~ s/new_data/$new_date/gi;

	$main =~ s/today_data/$today/gi;
	$main =~ s/yesterday_data/$yesterday/gi;
	$main =~ s/dbyday_data/$dbyesterday/gi;

	$main =~ s/cgi_data/$cgi/gi;
	$main =~ s/master_pass/$FORM{'pass'}/gi;

	$main =~ s/log_view/$log_view/gi;
	$main =~ s/ref_view/$ref_view/gi;
	$main =~ s/key_view/$key_view/gi;
	$main =~ s/doc_view/$doc_view/gi;
	$main =~ s/pixel_view/$pixel_view/gi;
	$main =~ s/agent_view/$agent_view/gi;
	$main =~ s/os_view/$os_view/gi;
	$main =~ s/host_view/$host_view/gi;

	$main =~ s/years_data/$years/gi;
	$main =~ s/mon_data/$mon/gi;

	if ($main =~ /<!-- logdir_html -->/i) {
		foreach (@log_dir) {
			if ($_ eq '') { next; }
			($key, $value) = split(/<>/, $_);
			if ($FORM{'logdir'} eq $key) {
				print qq{<option value="$key" selected="selected">$key</option>\n};
			} else { print qq{<option value="$key">$key</option>\n}; }
		}
	}

	if ($FORM{'word'}) {
		$main =~ s/name=\"word\" value=\"\"/name=\"word\" value=\"$FORM{'word'}\"/gi;
		$main =~ s/�́A����܂ł�.*?���B/�����L�^�������O�t�@�C���̌������ʂł��B/gi;
		$main =~ s/���� <em>/�������� <em>/gi;
	}

	if ($FORM{'mode'} eq 'or') {
		$main =~ s/name=\"mode\" value=\"or\"/name=\"mode\" value=\"or\" checked=\"checked\"/gi;
	} else {
		$main =~ s/name=\"mode\" value=\"and\"/name=\"mode\" value=\"and\" checked=\"checked\"/gi;
	}

	if ($do_view) { $main =~ s/name=\"do\"/name=\"do\" checked=\"checked\"/gi; }
	if ($ua_view) { $main =~ s/name=\"ua\"/name=\"ua\" checked=\"checked\"/gi; }
	if ($ip_view) { $main =~ s/name=\"ip\"/name=\"ip\" checked=\"checked\"/gi; }
	if ($rt_view) { $main =~ s/name=\"rt\"/name=\"rt\" checked=\"checked\"/gi; }
	if ($jp_view) { $main =~ s/name=\"jp\"/name=\"jp\" checked=\"checked\"/gi; }
	if ($se_view) { $main =~ s/name=\"se\"/name=\"se\" checked=\"checked\"/gi; }
	if ($se_view) { $main =~ s/name=\"sepl\" value=\"\"/name=\"sepl\" value=\"on\"/gi; }
	if ($keys_mode) { $main =~ s/name=\"keys\"/name=\"keys\" checked=\"checked\"/gi; }

	if ($ua_others) { $main =~ s/name=\"uao\"/name=\"uao\" checked=\"checked\"/gi; }
	if ($os_others) { $main =~ s/name=\"oso\"/name=\"oso\" checked=\"checked\"/gi; }
	if ($ip_count) { $main =~ s/name=\"ipc\"/name=\"ipc\" checked=\"checked\"/gi; }

	$main =~ s/class=\"uac\" value=\"$ua_count\"/class=\"uac\" value=\"$ua_count\" selected=\"selected\"/gi;

}

#=====================================================================
# HTML���쌠�\��

sub copy {

print <<"_END_";
<!-- $ver ���쌠�\\�� -->
original�F<a href="http://www.kent-web.com/" title="http://www.kent-web.com/">KENT WEB</a>
<!-- $acver ���쌠�\\�� -->
modified�F<a href="http://air.vis.ne.jp/at-works/" title="http://air.vis.ne.jp/at-works/">at works</a>
<!-- ���쌠�\\�������܂� -->
_END_

}

#=====================================================================
# stop

sub stop {

	&unlock if ($lockflag);
	print "Content-Type: text/plain\n\n";
	exit;

}

#=====================================================================
# �G���[����

sub error {

	&unlock if ($lockflag);
	&head;

print <<"_END_";
<div class="main">
<p><strong>ERROR !</strong></p>
<p><em>$_[0]</em></p>
</div>

</body>
</html>
_END_

	exit;

}

#=====================================================================
# �p�X���[�h���͉��

sub password {

	&cookie_get;
	&head;

	print "<p>\n";
	&copy;

print <<"_END_";
</p>

<div class="main">
<form action="$cgi" method="post">
<p>Password �F <input type="password" name="pass" size="8" value="$COOKIE{'pass'}" tabindex="1" accesskey="p" /> <input type="submit" value=" click " tabindex="2" /></p>
</form>
</div>

</body>
</html>
_END_

	exit;

}

#=====================================================================
# �`�F�b�N���[�h

sub check {

# ���O�t�@�C��
	$logfile = "$data_dir"."$logfile";

	if ($lockkey) {

		if (-e $lock_dir) { $lde_check = 'OK'; } else { $lde_check = 'NG'; }
		if (-r $lock_dir) { $ldr_check = 'OK'; } else { $ldr_check = 'NG'; }
		if (-w $lock_dir) { $ldw_check = 'OK'; } else { $ldw_check = 'NG'; }
		if (-x $lock_dir) { $ldx_check = 'OK'; } else { $ldx_check = 'NG'; }

	} else { $lde_check = $ldr_check = $ldw_check = $ldx_check = '---'; }

	if (-e $data_dir) { $dde_check = 'OK'; } else { $dde_check = 'NG'; }
	if (-r $data_dir) { $ddr_check = 'OK'; } else { $ddr_check = 'NG'; }
	if (-w $data_dir) { $ddw_check = 'OK'; } else { $ddw_check = 'NG'; }
	if (-x $data_dir) { $ddx_check = 'OK'; } else { $ddx_check = 'NG'; }

	if (-e $logfile) { $lfe_check = 'OK'; } else { $lfe_check = 'NG'; }
	if (-r $logfile) { $lfr_check = 'OK'; } else { $lfr_check = 'NG'; }
	if (-w $logfile) { $lfw_check = 'OK'; } else { $lfw_check = 'NG'; }

	if (-e $checkpl) { $cp_check = 'OK'; } else { $cp_check = 'NG'; }
	if (-e $titlepl) { $tp_check = 'OK'; } else { $tp_check = 'NG'; }
	if (-e $searchpl) { $se_check = 'OK'; } else { $se_check = 'NG'; }
	if (-e $agentpl) { $ap_check = 'OK'; } else { $ap_check = 'NG'; }
	if (-e $jcode) { $jc_check = 'OK'; } else { $jc_check = 'NG'; }
	if (-e $main_html) { $mh_check = 'OK'; } else { $mh_check = 'NG'; }

	&head;

	print "<p>\n";
	&copy;

print <<"_END_";
</p>

<div>
<table border="1" cellpadding="10" cellspacing="0" summary="check" class="check">

<thead>
	<tr>
	<th abbr="����">����</th>
	<th abbr="�ݒ�">�ݒ�</th>
	<th abbr="����">����</th>
	<th abbr="�Ǎ�">�Ǎ�</th>
	<th abbr="����">����</th>
	<th abbr="���s">���s</th>
	</tr>
</thead>

<tbody>

	<tr>
	<th align="right" abbr="lockkey">lockkey �F</th>
	<td>$lockkey</td>
	<td>---</td>
	<td>---</td>
	<td>---</td>
	<td>---</td>
	</tr>

	<tr>
	<th align="right" abbr="lock_dir">lock_dir �F</th>
	<td align="left">$lock_dir</td>
	<td>$lde_check</td>
	<td>$ldr_check</td>
	<td>$ldw_check</td>
	<td>$ldx_check</td>
	</tr>

	<tr>
	<th align="right" abbr="data_dir">data_dir �F</th>
	<td align="left">$data_dir</td>
	<td>$dde_check</td>
	<td>$ddr_check</td>
	<td>$ddw_check</td>
	<td>$ddx_check</td>
	</tr>

	<tr>
	<th align="right" abbr="logfile">logfile �F</th>
	<td align="left">$logfile</td>
	<td>$lfe_check</td>
	<td>$lfr_check</td>
	<td>$lfw_check</td>
	<td>---</td>
	</tr>

	<tr>
	<th align="right" abbr="checkpl">checkpl �F</th>
	<td align="left">$checkpl</td>
	<td>$cp_check</td>
	<td>---</td>
	<td>---</td>
	<td>---</td>
	</tr>

	<tr>
	<th align="right" abbr="titlepl">titlepl �F</th>
	<td align="left">$titlepl</td>
	<td>$tp_check</td>
	<td>---</td>
	<td>---</td>
	<td>---</td>
	</tr>

	<tr>
	<th align="right" abbr="searchpl">searchpl �F</th>
	<td align="left">$searchpl</td>
	<td>$se_check</td>
	<td>---</td>
	<td>---</td>
	<td>---</td>
	</tr>

	<tr>
	<th align="right" abbr="agentpl">agentpl �F</th>
	<td align="left">$agentpl</td>
	<td>$ap_check</td>
	<td>---</td>
	<td>---</td>
	<td>---</td>
	</tr>

	<tr>
	<th align="right" abbr="jcode">jcode �F</th>
	<td align="left">$jcode</td>
	<td>$jc_check</td>
	<td>---</td>
	<td>---</td>
	<td>---</td>
	</tr>

	<tr>
	<th align="right" abbr="main_html">main_html �F</th>
	<td align="left">$main_html</td>
	<td>$mh_check</td>
	<td>---</td>
	<td>---</td>
	<td>---</td>
	</tr>

</tbody>

</table>
</div>

<div>
<table border="1" cellpadding="10" cellspacing="0" summary="version" class="version">

<thead>
	<tr>
	<th abbr="����">����</th>
	<th abbr="�ݒu��">�ݒu��</th>
	</tr>
</thead>

<tbody>

	<tr>
	<th align="right" abbr="server">server �F</th>
	<td align="left">$ENV{'SERVER_SOFTWARE'}</td>
	</tr>

	<tr>
	<th align="right" abbr="Perl">Perl �F</th>
	<td align="left">$]</td>
	</tr>

	<tr>
	<th align="right" abbr="script">script �F</th>
	<td align="left">$acver</td>
	</tr>

</tbody>

</table>
</div>

</body>
</html>
_END_

	exit;

}

#=====================================================================
# HTML�w�b�_

sub head {

	print "Content-Type: text/html\n\n";

print <<"_END_";
<?xml version="1.0" encoding="Shift_JIS"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ja">
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=Shift_JIS" />
	<meta http-equiv="Content-Style-Type" content="text/css" />
	<link rel="stylesheet" type="text/css" title="access cgi" href="$css_dir/check.css" media="screen, print" />
	<title>access cgi</title>
</head>
<body>

_END_

}

#=====================================================================
