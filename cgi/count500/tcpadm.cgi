#!/usr/bin/perl
#
######################################################################
###
###
###  CGI�J�E���^�[ TcounT Ver.5.03
###     [2/2] �Ǘ� (tcpadm.cgi)
###                                 (c) 1996-2004 Takahiro Nishida
###                                 http://www.mytools.net/
###
###
######################################################################
#
### �ϐ��ݒ蕔 �i�ڍׂ͏�L�y�[�W�������������j ######################

# �Ǘ��p�X���[�h
$password = "yt112";
# �Ǘ��҃��[���A�h���X
$admin_email = "info\@gamelink.jp";
# �f�[�^�t�@�C���̊i�[�ʒu
$basedir = ".";
# �u�߂�v���������Ƃ��Ɉړ�����URL
$backurl = "http://www.gamelink.jp/";

### �ϐ��ݒ蕔 �i�����܂Łj###########################################

# ���O�{���Ƀp�X���[�h��v���邩�i1���K�v�A0���s�K�v�j
$NEED_PASSWORD_FOR_LOGVIEW = 0;
# �u�ŋ߁~���Ԃ̏W�v�v���������ɂ���
$RECENT_DAYS_COUNT = 7;
# �J�E���g�J�n����́~���𓝌v�Ώۂ��珜�O����
$AVG_IGNORE_DAYS_COUNT = 1;


$lockfile = "$basedir/lockdir/tc.lock";
$allfile = "$basedir/tcdall.txt";
$ystfile = "$basedir/tcdyst.txt";
$hstfile = "$basedir/tcdhst.txt";
$logfile = "$basedir/tcdlog.txt";
$bakfile = "$basedir/tcdbak.txt";

$verno = "5.03";

print "Content-type: text/html; Charset=shift_jis\n\n";

&main;

sub main{
	&lock;
	&init_variables;
	&open_datafile;
	&check_input;
	&exec_action;
	&update_files;
	&show_html;
	&unlock;
}



########## �ϐ��̏�����
sub init_variables{
	$noact = "�����ύX����܂���ł����B";
	$actmsg = "";
	
}



########## �f�[�^�t�@�C���̃I�[�v��
sub open_datafile{
	&openfile($allfile, *tdys);
	&openfile($ystfile, *ysts);
	
	### ���t�f�[�^�擾
	$g_date_rec = shift(@tdys);
	### �擾�ł��Ȃ�������recover�ň�U������
	($g_date_rec) || &error(391, "��� <A HREF=\"./tc.cgi?hoge\">������</A> ���N���b�N���ăf�[�^�t�@�C���̏��������s���A�ēx <A HREF=\"./tcpadm.cgi\">tcpadm.cgi</A> �ɃA�N�Z�X���Ă��������B");
	
	### �����f�[�^�̃n�b�V����
	foreach(@tdys){
		(/^\w+\t/) || next;
		($b_ccode) = split("\t");
		($b_ccode =~ /^\w+/) || next;
		$CTDY{$b_ccode} = $_;
		### �\�[�g���擾
		push(@g_codesort, $b_ccode);
	}
	
	### ����f�[�^�̃n�b�V����
	foreach(@ysts){
		($b_ccode) = split("\t");
		($CYST{$b_ccode} = $_);
	}
	
	### �����̃J�E���g��
	foreach (@g_codesort){
		($b_ccode, $b_ca, $b_cah) = split("\t", $CTDY{$_});
		($b_ccode, $b_cy, $b_cyh, $b_cu, $b_cuh) = split("\t", $CYST{$_});
		
		### �����������|�����
		$CCT{$_} = $b_ca - $b_cu;
		$CCTH{$_} = $b_cah - $b_cuh;
	}
}



########## ���͓��e�̃`�F�b�N
sub check_input{
	local($buffer, $vn, $pair, @pairs);
	
	if ($ENV{'REQUEST_METHOD'} eq "POST") {
		read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'});
	}
	else {
		$buffer = $ENV{'QUERY_STRING'};
	}
	@pairs = split(/&/, $buffer);
	foreach $pair (@pairs) {
		($vn, $value) = split(/=/, $pair);
		$F{$vn} .= $value;
	}
	
	$m_pwd = $F{'pwd'};
	$m_mode = $F{'mode'};
	$m_act = $F{'act'};
	$m_ccode = $F{'ccode'};
	(!$m_ccode) || ($m_ccode =~ /^\w+$/) || &error(300, "�J�E���^�[�̃R�[�h�����s���ł��F$m_ccode");
}



########## ��Ƃ̎��s
sub exec_action{
	### �p�X���[�h�`�F�b�N
	if ($m_pwd ne $password){
		$actmsg = ($m_pwd) ? "�p�X���[�h���Ԉ���Ă��܂��B$noact" : "��Ƃ�I�����A�p�X���[�h����͂��āu��Ǝ��s�v�������Ă��������B";
		### log���[�h����Password�s�v�u�łȂ��v�ꍇ�̓��[�h��top�ɖ߂�
		($m_mode eq 'log') && ($NEED_PASSWORD_FOR_LOGVIEW == 0) || ($m_mode = "top");
	}
	
	### mode���Ƃ̏�����
	if($m_mode eq 'cnt'){
		$actmsg = "�J�E���^�C���p�t�H�[����\\�����Ă��܂��B";
		if($m_act eq 'new' || $m_act eq 'fix'){
			&fix_data;
		}
	}
	elsif($m_mode eq 'log'){
		$actmsg = "�J�E���^�[���O��\\�����Ă��܂��B";
	}
	elsif($m_mode eq 'clm'){
		&clear_actlog;
		$actmsg = "�J�E���^�[���샍�O���N���A���܂����B";
	}
}



########## �f�[�^�̏C��
sub fix_data{
	local($m_ccode, $m_cdel);
	local($m_ca, $m_cah, $m_cy, $m_cyh, $m_cu, $m_cuh);
	local($newtdys, $newysts);
	
	### ���͂̎󂯎��
	$m_ccode = $F{'ccode'};
	$m_ca = $F{'ca'};
	$m_cu = $F{'cu'};
	$m_cy = $F{'cy'};
	$m_cah = $F{'cah'};
	$m_cuh = $F{'cuh'};
	$m_cyh = $F{'cyh'};
	$m_cdel = ($F{'cdel'}) ? 1 : 0;
	
	### ���͂̃`�F�b�N
	($m_ccode =~ /^\w+$/) || &error(300, "�J�E���^�[�R�[�h���s���ł��F�g�p�ł��镶���� [A-Za-z0-9] �ł�");
	($m_ca =~ /^\d+$/) || &error(301, "���͂��s���ł��F�u�q�׃A�N�Z�X���|���݁v�͔��p�����ŋL��");
	($m_cu =~ /^\d+$/) || &error(302, "���͂��s���ł��F�u�q�׃A�N�Z�X���|����܂Łv�͔��p�����ŋL��");
	($m_cy =~ /^\d+$/) || &error(303, "���͂��s���ł��F�u�q�׃A�N�Z�X���|����v�͔��p�����ŋL��");
	($m_cah =~ /^\d+$/) || &error(304, "���͂��s���ł��F�u�z�X�g�A�N�Z�X���|���݁v�͔��p�����ŋL��");
	($m_cuh =~ /^\d+$/) || &error(305, "���͂��s���ł��F�u�z�X�g�A�N�Z�X���|����܂Łv�͔��p�����ŋL��");
	($m_cyh =~ /^\d+$/) || &error(306, "���͂��s���ł��F�u�z�X�g�A�N�Z�X���|����v�͔��p�����ŋL��");
	
	### �Љ�I�G���[
	($m_ca >= $m_cu) || &error(307, "���l���s���ł��F���׃A�N�Z�X���|����($m_ca)������܂�($m_cu)��菬����");
	($m_cu >= $m_cy) || &error(309, "���l���s���ł��F���׃A�N�Z�X���|����܂�($m_cu)�����($m_cy)��菬����");
	($m_cah >= $m_cuh) || &error(308, "���l���s���ł��F�z�X�g�A�N�Z�X���|����($m_cah)������܂�($m_cuh)��菬����");
	($m_cuh >= $m_cyh) || &error(310, "���l���s���ł��F�z�X�g�A�N�Z�X���|����܂�($m_cuh)�����($m_cyh)��菬����");
	
	### �V�K
	if($m_act eq 'new')
	{
		($m_ccode) || &error(311, "�J�E���^�[�R�[�h�����͂���Ă��܂���B");
		($CTDY{$m_ccode}) && &error(312, "�w�肳�ꂽ�J�E���^�R�[�h�͊��Ɏg�p����Ă��܂��F$m_ccode");
		$actmsg = "�J�E���^ $m_ccode ��V�K�쐬���܂����B";
		push(@g_codesort, $m_ccode);
		$F{'cread'} = 0;
	}
	### �C��
	else{
		($CTDY{$m_ccode}) || &error(313, "�w�肳�ꂽ�J�E���^�R�[�h�͑��݂��܂���F$m_ccode");
		$actmsg = "�J�E���^ $m_ccode ���C�����܂����B";
		$F{'cread'} = 1;
		### �폜
		if($m_cdel)
		{
			foreach(0..$#g_codesort)
			{
				($g_codesort[$_] eq $m_ccode) && splice(@g_codesort, $_, 1);
			}
			$actmsg = "�J�E���^ $m_ccode ���폜���܂����B";
			$F{'cread'} = 0;
		}
	}
	### �n�b�V���쐬 or �㏑��
	$CTDY{$m_ccode} = "$m_ccode\t$m_ca\t$m_cah\t\n";
	$CYST{$m_ccode} = "$m_ccode\t$m_cy\t$m_cyh\t$m_cu\t$m_cuh\t\n";
	
	### �����������|�����
	$CCT{$m_ccode} = $m_ca - $m_cu;
	$CCTH{$m_ccode} = $m_cah - $m_cuh;
	
	### �f�[�^�ĕҐ�
	push(@newtdys, $g_date_rec); # ���t
	foreach(@g_codesort)
	{
		### �s�}��
		push(@newtdys, $CTDY{$_});
		push(@newysts, $CYST{$_});
	}
	@tdys = @newtdys;
	@ysts = @newysts;
	
	### �X�V�t���O
	$upf_tdys = 1;
	$upf_ysts = 1;
}



########## �J�E���^�[���샍�O�̃N���A
sub clear_actlog{
	local @tmps = ();
	&updatefile($logfile, *tmps);
}



########## �t�@�C���̍X�V
sub update_files{
	($upf_tdys) && &updatefile($allfile, *tdys);
	($upf_ysts) && &updatefile($ystfile, *ysts);
}



########## �\��
sub show_html{
	local($hbuf_copyright, $hbuf_table, $hbuf_form);
	
	($F{'back'}) && ($m_mode = "top");
	
	if($m_mode eq 'cnt'){
		$hbuf_table = &html_table;
		$hbuf_form = &html_form;
	}
	elsif($m_mode eq 'log'){
		$hbuf_table = &html_log;
	}
	else{
		$hbuf_form = &html_top;
	}
	
	$hbuf_copyright = &copyright;
	
	print <<EOP
	<HTML>
	<HEAD>
	<TITLE>T-Count 5 - �Ǘ��p�y�[�W</TITLE>
	<STYLE TYPE=\"text/css\">
	<!--
	A{ text-decoration:none; }
	TD{ font-size:12px; text-align:center; }
	TH{ font-size:12px; text-align:center; font-weight:bold; }
	TD.head{ color:#000000; background-color:#FFFFCC; text-align:center; font-weight:bold; }
	TD.form{ color:#000000; background-color:#FFFFFF; }
	TD.comm{ color:#000000; background-color:#FFFFCC; text-align:left; }
	CAPTION{ font-size:13px; text-align:left; }
	
	TH.key{ font-size:12px; font-weight:bold; color:#FFFFFF; background-color:#660000; }
	.attention{ font-size:11px; }
	
	.d { color:#000000; }
	.dh{ color:#0000AA; }
	.dd{ font-size:10px; color:#555555; }
	.u { color:#000000; }
	.uh{ color:#0000AA; }
	.weak { font-size:11px; color:#FF3300; }
	.emp { color:#FF0000; font-weight:bold; }
	
	.w0 { color:#000000; background-color:#FFCCCC; }
	.w1 { color:#000000; background-color:#FFFFFF; }
	.w2 { color:#000000; background-color:#FFFFFF; }
	.w3 { color:#000000; background-color:#FFFFFF; }
	.w4 { color:#000000; background-color:#FFFFFF; }
	.w5 { color:#000000; background-color:#FFFFFF; }
	.w6 { color:#000000; background-color:#CCCCFF; }
	.ws { color:#000000; background-color:#CCFFCC; }
	.m { color:#000000; background-color:#FFFF99; font-weight:bold; }
	
	-->
	</STYLE>
	</HEAD>
	<BODY BGCOLOR=\"#FF9999\">
	<FONT SIZE=\"2\">
	[<A HREF=\"$backurl\">�߂�</A>]
	[<A HREF=\"tcpadm.cgi\">�Ǘ��g�b�v</A>]
	
	<H3>T-Count 5 �Ǘ��p�y�[�W</H3>
	<HR SIZE=\"1\" NOSHADE>
	<B>��Ə󋵁F</B> $actmsg
	<HR SIZE=\"1\" NOSHADE>
	$hbuf_form
	$hbuf_table
	<HR SIZE=\"1\" NOSHADE>
	<DIV ALIGN=\"right\">$hbuf_copyright</DIV>
	</BODY>
	</HTML>
EOP
}



########## �g�b�v���
sub html_top{
	local($hbuf_logview);
	
	($NEED_PASSWORD_FOR_LOGVIEW == 0) && ($hbuf_logview = "<SPAN CLASS=\"weak\">���p�X���[�h�s�v��</SPAN>");
	
	"
	<FORM METHOD=\"post\" ACTION=\"tcpadm.cgi\">
	�p�X���[�h<INPUT TYPE=\"password\" NAME=\"pwd\" SIZE=\"15\" VALUE=\"$m_pwd\">
	<INPUT TYPE=\"submit\" VALUE=\"��Ǝ��s\"><BR>
	<INPUT TYPE=\"radio\" NAME=\"mode\" VALUE=\"log\" CHECKED>�J�E���^���O�A���샍�O�{��&nbsp;&nbsp;$hbuf_logview<BR>
	<INPUT TYPE=\"radio\" NAME=\"mode\" VALUE=\"cnt\">�J�E���^�V�K�쐬�A�C���A�폜<BR>
	<INPUT TYPE=\"radio\" NAME=\"mode\" VALUE=\"clm\">���샍�O�̃N���A<BR>
	</FORM>
	";
}



########## �C���p�t�H�[��
sub html_form{
	local($b_ccode, $b_ca, $b_cah);
	local($b_ccode, $b_cy, $b_cyh, $b_cu, $b_cuh);
	
	### �v���_�E��
	foreach(@g_codesort)
	{
		($b_selected) = ($_ eq $m_ccode) ? "SELECTED" : "";
		$hbuf_options .= "<OPTION " . $b_selected . ">" . $_ . "\n";
	}
	
	### �ǂݍ��݂̏ꍇ
	if($F{'cread'})
	{
		($m_ccode) || &error(8, "�R�[�h���w�肳��Ă��܂���");
		($b_ccode, $b_ca, $b_cah) = split("\t", $CTDY{$m_ccode});
		($b_ccode, $b_cy, $b_cyh, $b_cu, $b_cuh) = split("\t", $CYST{$m_ccode});
		$b_act = "fix";
		$b_title = "$m_ccode �C��";
		$hbuf_ccode = "<INPUT TYPE=\"hidden\" NAME=\"ccode\" VALUE=\"$m_ccode\">$m_ccode &nbsp;&nbsp;&nbsp;<SPAN CLASS=\"weak\">�i���ύX�s���j</SPAN>";
		$hbuf_del = "<INPUT TYPE=\"checkbox\" NAME=\"cdel\" VALUE=\"1\">���̃J�E���^���폜&nbsp;&nbsp;&nbsp;";
	}
	### �V�K�쐬�̏ꍇ
	else
	{
		($b_ca, $b_cah, $b_cy, $b_cyh, $b_cu, $b_cuh) = (0, 0, 0, 0, 0, 0);
		$b_act = "new";
		$b_title = "�V�K�o�^";
		$hbuf_ccode = "<INPUT TYPE=\"text\" NAME=\"ccode\" SIZE=\"15\">&nbsp;&nbsp;&nbsp;<SPAN CLASS=\"weak\">�i�����p�p�������j</SPAN>";
	}
	
	$htmlbuf .= "
		<FORM METHOD=\"post\" ACTION=\"tcpadm.cgi\">
		<INPUT TYPE=\"hidden\" NAME=\"pwd\" VALUE=\"$m_pwd\">
		<INPUT TYPE=\"hidden\" NAME=\"mode\" VALUE=\"cnt\">
		<DIV ALIGN=\"center\">
		<TABLE WIDTH=\"70%\" BORDER=\"1\" CELLPADDING=\"1\" CELLSPACING=\"0\" BGCOLOR=\"#FFFFFF\">
		<TR><TH CLASS=\"key\">
		�J�E���^
		<SELECT NAME=\"ccode\" SIZE=\"1\">
		$hbuf_options
		</SELECT>
		��
		<INPUT TYPE=\"submit\" NAME=\"cread\" VALUE=\"�ǂݍ���\"> or 
		<INPUT TYPE=\"submit\" NAME=\"cnew\" VALUE=\"�V�K�o�^\">
		&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
		<INPUT TYPE=\"submit\" NAME=\"back\" VALUE=\"���߂�\">
		</FONT></TD></TR></TABLE>
		</DIV>
		</FORM>
		<P>
	";
	
	$htmlbuf .= "
		<FORM METHOD=\"post\" ACTION=\"tcpadm.cgi\">
		<INPUT TYPE=\"hidden\" NAME=\"pwd\" VALUE=\"$m_pwd\">
		<INPUT TYPE=\"hidden\" NAME=\"mode\" VALUE=\"cnt\">
		<INPUT TYPE=\"hidden\" NAME=\"act\" VALUE=\"$b_act\">
		<DIV ALIGN=\"center\">
		<TABLE WIDTH=\"80%\" BORDER=\"1\" CELLPADDING=\"1\" CELLSPACING=\"0\" BGCOLOR=\"#FFFFFF\">
		<TR><TH CLASS=\"key\" COLSPAN=\"2\"><FONT COLOR=\"#FFFFFF\">�� �J�E���^ $b_title ��</FONT></TH></TR>
		<TR><TD CLASS=\"head\">�J�E���^�[�R�[�h</TH>
		<TD CLASS=\"form\">$hbuf_ccode</TD></TR>
		<TR><TD CLASS=\"head\">���׃A�N�Z�X��</TH>
		<TD CLASS=\"form\">
			���݁�<INPUT TYPE=\"text\" NAME=\"ca\" SIZE=\"8\" VALUE=\"$b_ca\">�A
			����܂Ł�<INPUT TYPE=\"text\" NAME=\"cu\" SIZE=\"8\" VALUE=\"$b_cu\">�A
			�����<INPUT TYPE=\"text\" NAME=\"cy\" SIZE=\"5\" VALUE=\"$b_cy\">
		</TD>
		</TR>
		<TR><TD CLASS=\"head\">�z�X�g�A�N�Z�X��</TH>
		<TD CLASS=\"form\">
			���݁�<INPUT TYPE=\"text\" NAME=\"cah\" SIZE=\"8\" VALUE=\"$b_cah\">�A
			����܂Ł�<INPUT TYPE=\"text\" NAME=\"cuh\" SIZE=\"8\" VALUE=\"$b_cuh\">�A
			�����<INPUT TYPE=\"text\" NAME=\"cyh\" SIZE=\"5\" VALUE=\"$b_cyh\">
		</TD>
		</TR>
		<TR><TH COLSPAN=\"2\" CLASS=\"key\">
		$hbuf_del
		<INPUT TYPE=\"submit\" NAME=\"exec\" VALUE=\"��Ǝ��s\">
		</FONT></TH></TR>
		<TR><TD CLASS=\"comm\" COLSPAN=\"2\">
		�� ���׃A�N�Z�X�� �c �y�[�W���J���ꂽ�񐔁i���J�E���^�̐����摜���\\�����ꂽ�񐔁j<BR>
		�� �z�X�g�A�N�Z�X�� �c �������̓���z�X�g����̃A�N�Z�X����x�����J�E���g���Ȃ��ꍇ�̉�<BR>
		�� �u�����v�̐��l�́u���݁|����܂Łv�ŎZ�o���Ă��܂��B<BR>
		�� �����ł̏C���͏W�v�ς݂̉ߋ����O�ɂ͈�؉e����^���܂���B���݂̊i�[�l��ς��邾���ł��B<BR>
		</TD></TR>
		
		</TABLE>
		</DIV>
		</FORM>
		<BR><BR>
	";
	
}



########## �J�E���^�ꗗ
sub html_table{
	local($htmlbuf, $b_ccode, );
	
	$htmlbuf = "
	<DIV ALIGN=\"center\">
	<TABLE WIDTH=\"80%\" BORDER=\"1\" CELLPADDING=\"1\" CELLSPACING=\"0\">
	<CAPTION>
	<B>�o�^���ꗗ</B><BR>
	</CAPTION>
	<TR BGCOLOR=\"330000\">
	<TH CLASS=\"key\">code</TH>
	<TH CLASS=\"key\">�݌v</TH>
	<TH CLASS=\"key\">�݌vH</TH>
	<TH CLASS=\"key\">����</TH>
	<TH CLASS=\"key\">����H</TH>
	<TH CLASS=\"key\">���</TH>
	<TH CLASS=\"key\">���H</TH>
	<TH CLASS=\"key\">�e�X�g</TH>
	</TR>
	";
	
	$i = 0;
	$bgs[0] = "#FFCCCC";
	$bgs[1] = "#FFFFFF";
	
	foreach (@g_codesort){
		($b_ccode, $b_ca, $b_cah) = split("\t", $CTDY{$_});
		($b_ccode, $b_cy, $b_cyh, $b_cu, $b_cuh) = split("\t", $CYST{$_});
		
		$htmlbuf .= "
		<TR BGCOLOR=\"$bgs[$i%2]\">
		<TH>
		<SPAN CLASS=\"emp\">$b_ccode</SPAN></TH>
		<TD>$b_ca<A HREF=\"./tc.cgi?$b_ccode&a\">[C]</A></TD>
		<TD>$b_cah<A HREF=\"./tc.cgi?$b_ccode&ah\">[C]</A></TD>
		<TD>$CCT{$_}<A HREF=\"./tc.cgi?$b_ccode&t\">[C]</A></TD>
		<TD>$CCTH{$_}<A HREF=\"./tc.cgi?$b_ccode&th\">[C]</A></TD>
		<TD>$b_cy<A HREF=\"./tc.cgi?$b_ccode&y\">[C]</A></TD>
		<TD>$b_cyh<A HREF=\"./tc.cgi?$b_ccode&yh\">[C]</A></TD>
		<TD>
		[<A HREF=\"./tc.cgi?$b_ccode&a&1\">Up</A>]
		</TD>
		</TR>
		";
		
		$i++;
	}
	
	$htmlbuf .= "
		<TR><TD CLASS=\"comm\" COLSPAN=\"8\">
		�� \"H\"�̓z�X�g�A�N�Z�X���̓��v�i�ڂ����͏�L�j<BR>
		�� \"[C]\"���N���b�N����ƃJ�E���^�摜���\\������܂��B�^�O�̊m�F�Ȃǂɂ��g���������B<BR>
		�� \"Up\"���N���b�N����ƃJ�E���g�����������܂��B����m�F�ɂ��g���������B<BR>
		�� �X�C�b�`�̎d�l �� �R�[�h&���&����&�摜&����<BR>
		</TD></TR>
	";
	$htmlbuf .= "</TABLE></DIV>";
}



########## �J�E���^���O
sub html_log{
	local($htmlbuf, $hbuf_header, $hbuf_comment, $hbuf_day, $hbuf_month, $hbuf_all);
	local($b_ccode, $b_ca, $b_cah, $b_cd, $b_cdh, $b_cu, $b_cuh, $b_pmon, $b_date);
	local(@b_dayhsts, %IH, %DH, %MH, %AH);
	
	### ���O�t�@�C�����J��
	&openfile($hstfile, *hsts);
	### �t���ɂ�����������������폜
	foreach(@hsts)
	{
		($b_date, @b_dayhsts) = split("\t");
		foreach $bh(@b_dayhsts)
		{
			($b_id) = split("/", $bh);
			(++$IH{$b_id} > $AVG_IGNORE_DAYS_COUNT) || next;
			$b_date .= "\t$bh";
		}
		unshift(@bhsts, $b_date);
	}
	@hsts = @bhsts;
	
	
	### �W�v����
	$b_begin = (split("\t", $hsts[$#hsts]))[0];
	$b_end   = (split("\t", $hsts[0]))[0];
	$b_begin =~ s/(\d{2})(\d{2})(\d{2})(\d{2})/$2\/$3\/$4/;
	$b_end   =~ s/(\d{2})(\d{2})(\d{2})(\d{2})/$2\/$3\/$4/;
	
	
	### �w�b�_�s
	$hbuf_header .= "<TR><TH CLASS=\"key\">Code = </TH>";
	foreach(@g_codesort){
		$hbuf_header .= "<TH CLASS=\"key\">$_</TH>";
	}
	$hbuf_header .= "</TR>\n";
	### �R�[�h��+1�icolspan�p�j
	$b_tcols = @g_codesort + 1;
	
	
	### �R�����g
	$hbuf_comment = "
		<DIV CLASS=\"attention\">
		���̃��O�t�@�C�������� �� <A HREF=\"./$bakfile\">�z�X�g���O</A> �^ <A HREF=\"./$logfile\">���샍�O</A><P>
		�� �\\���̌����F�u<SPAN CLASS=\"d\">���׃A�N�Z�X��</SPAN>�^<SPAN CLASS=\"dh\">�z�X�g�A�N�Z�X��</SPAN>�v�A(xxx)�͗݌v�A[xxx]�͓���<BR>
		�� ���׃A�N�Z�X�� �c �y�[�W���J���ꂽ�񐔁i���J�E���^�̐����摜���\\�����ꂽ�񐔁j<BR>
		�� �z�X�g�A�N�Z�X�� �c �������̓���z�X�g����̃A�N�Z�X����x�����J�E���g���Ȃ��ꍇ�̉�
		</DIV><P>
		";
	
	### ���P�ʕ\���w�b�_
	$hbuf_day .= "
		<DIV ALIGN=\"left\">
		<TABLE BORDER=\"0\" CELLPADDING=\"2\" CELLSPACING=\"1\" BGCOLOR=\"#330000\">
		<TR><TD COLSPAN=\"$b_tcols\" CLASS=\"comm\"><SPAN CLASS=\"emp\">�� ���ʓ��v</SPAN></TD></TR>
	";
	$hbuf_day .= $hbuf_header;
	
	### ���P�ʕ\���p�w�b�_
	$hbuf_month = "
		<DIV ALIGN=\"left\">
		<TABLE BORDER=\"0\" CELLPADDING=\"2\" CELLSPACING=\"1\" BGCOLOR=\"#330000\">
		<TR><TD COLSPAN=\"$b_tcols\" CLASS=\"comm\"><SPAN CLASS=\"emp\">�� ���ʓ��v</SPAN></TD></TR>
		";
	$hbuf_month .= $hbuf_header;
	
	### ���v�\���p�w�b�_
	$hbuf_all = "
		<DIV ALIGN=\"left\">
		<TABLE BORDER=\"0\" CELLPADDING=\"2\" CELLSPACING=\"1\" BGCOLOR=\"#330000\">
		<TR><TD COLSPAN=\"$b_tcols\" CLASS=\"comm\"><SPAN CLASS=\"emp\">�� �������v</SPAN>
		<SPAN CLASS=\"d\">�i$b_begin�`$b_end�j</SPAN></TD></TR>
		";
	$hbuf_all .= $hbuf_header;
	
	### �j���P�ʕ\���p�w�b�_
	$hbuf_week = "
		<DIV ALIGN=\"left\">
		<TABLE BORDER=\"0\" CELLPADDING=\"2\" CELLSPACING=\"1\" BGCOLOR=\"#330000\">
		<TR><TD COLSPAN=\"$b_tcols\" CLASS=\"comm\"><SPAN CLASS=\"emp\">�� �j���ʓ��v</SPAN></TD></TR>
		";
	$hbuf_week .= $hbuf_header;
	
	### �\���F����
	$hbuf_day .=  "<TR><TD CLASS=\"ws\">�i�����j</TD>";
	foreach(@g_codesort)
	{
		($b_ccode, $b_ca, $b_cah) = split("\t", $CTDY{$_});
		$hbuf_day .= "
			<TD CLASS=\"ws\">
			<SPAN CLASS=\"d\">$CCT{$_}</SPAN>/<SPAN CLASS=\"dh\">$CCTH{$_}</SPAN>
			(<SPAN CLASS=\"u\">$b_ca</SPAN>/<SPAN CLASS=\"uh\">$b_cah</SPAN>)
			</TD>
		";
	}
	$hbuf_day .= "</TR>\n";
	
	# �����芴�m�p
	$b_pmon = substr($hsts[0], 0, 6);
	# �ŋ߁~���ԃJ�E���g�p
	$b_rday = 0;
	# �_�~�[�s
	push(@hsts, "00000000");
	
	### �\���F����ȑO
	foreach(@hsts)
	{
		# ���t�̕���
		($b_date, @b_dayhsts) = split("\t");
		$b_sdate = $b_date;
		$b_sdate =~ s/(\d{2})(\d{2})(\d{2})(\d{2})/$2\/$3\/$4/;
		# �j���̎擾
		$b_wday = &date2wday($2, $3, $4);
		
		# �����ς������w�b�_�ĕ\��
		if($b_pmon ne substr($b_date, 0, 6))
		{
			($b_pmon) || last;
			substr($b_pmon, 4, 0, "/");
			
			$hbuf_month .= "<TR><TD CLASS=\"ws\">$b_pmon ����</TD>";
			
			# ������
			foreach(@g_codesort)
			{
				$b_cd = $MH{"T/$_"};
				$b_cdh = $MH{"TH/$_"};
				$b_cdd = $MH{"D/$_"} || "0";
				$hbuf_month .= "
					<TD CLASS=\"ws\">
					<SPAN CLASS=\"d\">$b_cd</SPAN>/<SPAN CLASS=\"dh\">$b_cdh</SPAN>
					<SPAN CLASS=\"dd\">[$b_cdd]</SPAN>
					</TD>
					";
			}
			$hbuf_month .= "</TR>\n";
			
			# ������
			$hbuf_month .= "<TR><TD CLASS=\"w3\">$b_pmon ����</TD>";
			foreach(@g_codesort)
			{
				($MH{"D/$_"}) || ($MH{"D/$_"} = 1);
				$b_cd = sprintf("%.2f", $MH{"T/$_"} / $MH{"D/$_"});
				$b_cdh = sprintf("%.2f", $MH{"TH/$_"} / $MH{"D/$_"});
				$hbuf_month .= "
					<TD CLASS=\"w3\">
					<SPAN CLASS=\"d\">$b_cd</SPAN>/<SPAN CLASS=\"dh\">$b_cdh</SPAN>
					</TD>
					";
			}
			$hbuf_month .= "</TR>\n";
			
			# ���̃w�b�_
			$hbuf_day .= $hbuf_header;
			# ��n��
			$b_pmon = substr($b_date, 0, 6);
			undef(%MH);
		}
		
		### ���t���I���_�~�[�ɒB���Ă�����I��
		($b_date eq "00000000") && last;
		
		# �����̃J�E���g
		undef(%DH);
		foreach(@b_dayhsts){
			($b_ccode) = split("/");
			# ����\������̂ň�U�n�b�V���ɓ����
			$DH{$b_ccode} = $_;
			# �����̃J�E���g
			$AH{"D/$b_ccode"}++;
			$MH{"D/$b_ccode"}++;
			$WH{"D/$b_wday/$b_ccode"}++;
			if($b_rday < $RECENT_DAYS_COUNT){
				$RH{"D/$b_ccode"}++;
			}
		}
		
		# ���t�̕\��
		$hbuf_day .= "<TR><TD CLASS=\"w$b_wday\">$b_sdate</TD>";
		
		foreach(@g_codesort){
			($b_ccode, $b_cd, $b_cdh, $b_cu, $b_cuh) = split("/", $DH{$_});
			$MH{"T/$_"} += $b_cd;
			$MH{"TH/$_"} += $b_cdh;
			$AH{"T/$_"} += $b_cd;
			$AH{"TH/$_"} += $b_cdh;
			$WH{"T/$b_wday/$_"} += $b_cd;
			$WH{"TH/$b_wday/$_"} += $b_cdh;
			if($b_rday < $RECENT_DAYS_COUNT){
				$RH{"T/$_"} += $b_cd;
				$RH{"TH/$_"} += $b_cdh;
			}
			if($b_cd){
				$hbuf_day .= "
					<TD CLASS=\"w$b_wday\">
					<SPAN CLASS=\"d\">$b_cd</SPAN>/<SPAN CLASS=\"dh\">$b_cdh</SPAN>
					(<SPAN CLASS=\"u\">$b_cu</SPAN>/<SPAN CLASS=\"uh\">$b_cuh</SPAN>)
					</TD>
					";
			}
			else{
				$hbuf_day .= "<TD CLASS=\"w$b_wday\"><SPAN CLASS=\"dd\">n/a</SPAN></TD>";
			}
		}
		$hbuf_day .= "</TR>\n";
		# �ŋ߂̓���
		($b_rday < $RECENT_DAYS_COUNT) && ($b_rday++);
	}
	$hbuf_day .= "</TABLE></DIV>";
	
	### ���P�ʁF����
	$hbuf_month .= "</TABLE></DIV><P>";
	
	### �����F���v
	$hbuf_all .= "<TR><TD CLASS=\"ws\">�S����</TD>";
	foreach(@g_codesort)
	{
		$b_cd = $AH{"T/$_"};
		$b_cdh = $AH{"TH/$_"};
		$b_cdd = $AH{"D/$_"} || "0";
		$hbuf_all .= "
			<TD CLASS=\"ws\">
			<SPAN CLASS=\"d\">$b_cd</SPAN>/<SPAN CLASS=\"dh\">$b_cdh</SPAN>
			<SPAN CLASS=\"dd\">[$b_cdd]</SPAN>
			</TD>
			";
	}
	$hbuf_all .= "</TR>";
	
	### �����F����
	$hbuf_all .= "<TR><TD CLASS=\"w3\">�S���ԁE����</TD>";
	foreach(@g_codesort)
	{
		($AH{"D/$_"}) || ($AH{"D/$_"} = 1);
		$b_cd = sprintf("%.2f", $AH{"T/$_"} / $AH{"D/$_"});
		$b_cdh = sprintf("%.2f", $AH{"TH/$_"} / $AH{"D/$_"});
		$hbuf_all .= "
			<TD CLASS=\"w3\">
			<SPAN CLASS=\"d\">$b_cd</SPAN>/<SPAN CLASS=\"dh\">$b_cdh</SPAN>
			</TD>
			";
	}
	$hbuf_all .= "</TR>";
	
	### �ŋ߁~���ԁF���v
	$hbuf_all .= "<TR><TD CLASS=\"ws\">�ŋ�$b_rday���ԁE���v</TD>";
	foreach(@g_codesort)
	{
		$b_cd = $RH{"T/$_"};
		$b_cdh = $RH{"TH/$_"};
		$hbuf_all .= "
			<TD CLASS=\"ws\">
			<SPAN CLASS=\"d\">$b_cd</SPAN>/<SPAN CLASS=\"dh\">$b_cdh</SPAN>
			</TD>
			";
	}
	$hbuf_all .= "</TR>";
	
	### �ŋ߁~���ԁF����
	$hbuf_all .= "<TR><TD CLASS=\"w3\">�ŋ�$b_rday���ԁE����</TD>";
	foreach(@g_codesort)
	{
		($RH{"D/$_"}) || ($RH{"D/$_"} = 1);
		$b_cd = sprintf("%.2f", $RH{"T/$_"} / $RH{"D/$_"});
		$b_cdh = sprintf("%.2f", $RH{"TH/$_"} / $RH{"D/$_"});
		$hbuf_all .= "
			<TD CLASS=\"w3\">
			<SPAN CLASS=\"d\">$b_cd</SPAN>/<SPAN CLASS=\"dh\">$b_cdh</SPAN>
			</TD>
			";
	}
	$hbuf_all .= "</TR></TABLE></DIV><P>";
	
	### �j����
	$WK[0] = "��"; $WK[1] = "��"; $WK[2] = "��"; $WK[3] = "��"; 
	$WK[4] = "��"; $WK[5] = "��"; $WK[6] = "�y"; 
	for($wd = 0; $wd<=6; $wd++)
	{
		$hbuf_week .= "<TR><TD CLASS=\"w$wd\">$WK[$wd]�j</TD>";
		foreach(@g_codesort)
		{
			$b_cd = $WH{"T/$wd/$_"};
			$b_cdh = $WH{"TH/$wd/$_"};
			$b_cdd = $WH{"D/$wd/$_"} || "0";
			$hbuf_week .= "
				<TD CLASS=\"ws\">
				<SPAN CLASS=\"d\">$b_cd</SPAN>/<SPAN CLASS=\"dh\">$b_cdh</SPAN>
				<SPAN CLASS=\"dd\">[$b_cdd]</SPAN>
				</TD>
				";
		}
		$hbuf_week .= "</TR><TR><TD CLASS=\"w$wd\">$WK[$wd]�j�E����</TD>";
		foreach(@g_codesort)
		{
			($WH{"D/$wd/$_"}) || ($WH{"D/$wd/$_"} = 1);
			$b_cd = sprintf("%.2f", $WH{"T/$wd/$_"} / $WH{"D/$wd/$_"});
			$b_cdh = sprintf("%.2f", $WH{"TH/$wd/$_"} / $WH{"D/$wd/$_"});
			$hbuf_week .= "
				<TD CLASS=\"w3\">
				<SPAN CLASS=\"d\">$b_cd</SPAN>/<SPAN CLASS=\"dh\">$b_cdh</SPAN>
				</TD>
				";
		}
	}
	$hbuf_week .= "</TR></TABLE></DIV><P>";
	
	
	### �\�����̌���
	$htmlbuf = $hbuf_comment . $hbuf_all . $hbuf_month . $hbuf_week . $hbuf_day;
	
	return $htmlbuf;
}



########## �R�s�[���C�g
sub copyright{
	"
<TABLE ALIGN=\"right\" BORDER=\"0\" CELLPADDING=\"1\" CELLSPACING=\"1\" BGCOLOR=\"#990000\">
<TR><TH BGCOLOR=\"#FFFFCC\">
<A HREF=\"http://www.mytools.net/\" TARGET=\"_top\">
<FONT SIZE=\"2\" COLOR=\"#660000\">Powered by T-Count Ver.$verno</A>
</FONT></TH></TR></TABLE>
	";
}



########## �t�@�C�����J���āA���g��z��ɑ������
sub openfile{
	local ($filename, *bufs, $frag) = @_;
	
	(-f $filename) || ($frag) || &error(981, "�t�@�C�������݂��܂���F$filename");
	open(FILE, "$filename") || ($frag) || &error(982, "�t�@�C����ǂݍ��݃��[�h�ŊJ�����Ƃ��ł��܂���F$filename");
	@bufs = <FILE>;
	close(FILE);
	
	(@bufs) ? return(1) : return(0);
}



########## �t�@�C�����X�V����
sub updatefile{
	local ($filename, *buf, $frag) = @_;
	
	(-f $filename) || &error(383, "�t�@�C�������݂��܂���F$filename");
	# �t���O���聨�ǉ��A�Ȃ����X�V
	if($frag){
		open(FILE, ">>$filename") || &error(384, "�t�@�C����ǋL���[�h�ŊJ�����Ƃ��ł��܂���F$filename");
	}
	else{
		open(FILE, ">$filename") || &error(385, "�t�@�C�����������݃��[�h�ŊJ�����Ƃ��ł��܂���F$filename");
	}
	print FILE @buf;
	close(FILE);
}



##### ���t���j���ϊ�
sub date2wday
{
	local($year, $mon, $day) = @_;
	if($mon < 3){ $year--; $mon += 12; }
	return ($year + int($year/4) - int($year/100) + int($year/400) + int((13 * $mon + 8) / 5) + $day) % 7;
}



##### �t�@�C�����b�N
sub lock
{
	local($try) = 5;
	while(!(mkdir($lockfile, 0700))){
		if(--$try > 0){
			&error(100, "���b�N���ł�");
		}
		sleep(3);
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
	local($code, $errmsg) = @_;
	local(@sts) = lstat($lockfile);
	local($tn) = time();
	
	print "
<HTML>
<HEAD><TITLE>T-Count 5 - Error!!</TITLE></HEAD>
<BODY BGCOLOR=\"#FFFFFF\">
<FONT SIZE=\"3\">
<H3>�G���[����</H3>
ERR-$code: 
<FONT COLOR=\"#FF0000\">$errmsg</FONT><P>
<HR NOSHADE SIZE=\"1\">
<FONT SIZE=\"2\">
<B>�Ǘ��ҁF<A HREF=\"mailto:$admin_email\">$admin_email</A></B><BR>
�� �����̍ۂɂ̓T�C�g�̂t�q�k�ƏǏ���������Y���������܂��悤���肢���܂��B
</FONT>
";
	
	($code == 100) || &unlock; # ID �� 100 �ȊO�̏ꍇ�̓��b�N����
	($tn - $sts[9] < 15) || &unlock; # ��15�b�ȏネ�b�N�������Ă��玩������
	exit;
}
