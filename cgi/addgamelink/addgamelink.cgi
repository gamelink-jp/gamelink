#!/usr/bin/perl

require "./error.pl";
require "./data.pl";
require "./jcode.pl";

#####
# error ����

if ($ENV{'REQUEST_METHOD'} eq "POST") {
  if ($ENV{'CONTENT_LENGTH'} > 5000) {
    $err_log = '����̤��礭�����ޤ���';
    &error($err_log);
  }
} else {
  $err_log = '���Υե������ľ�ܼ¹Ԥ�����ϤǤ��ޤ���';
  &error($err_log);
}

#####
# form����ǡ�������

&get_data();

# ���Ѥ�Ⱦ�Ѥ��Ѵ�
$from = '�ݡ�������������-����-�ڣ�-��';
$to   = '-.:_/~@0-9A-Za-z';
&jcode'tr(*maker_name, $from, $to);
&jcode'tr(*url, $from, $to);
&jcode'tr(*b_url, $from, $to);
&jcode'tr(*width, $from, $to);
&jcode'tr(*height, $from, $to);
&jcode'tr(*u_mail_ad, $from, $to);

# Ⱦ�ѥ��ʤ����ѥ��ʤ��Ѵ�
&jcode'h2z_euc(*maker_name);
&jcode'h2z_euc(*maker_name2);
&jcode'h2z_euc(*comment);
&jcode'h2z_euc(*user_name);

#####
# ɬ�����Ϲ��ܳ�ǧ
if ($who eq "") {
  $err_log = '[�����Ծ���]�����Ϥ���Ƥ��ޤ���';
  &error($err_log);
}
if ($maker_name eq "") {
  $err_log = '[�᡼����/�֥���̾] �����Ϥ���Ƥ��ޤ���';
  &error($err_log);
}
if ($url eq "") {
  $err_log = '[URL] �����Ϥ���Ƥ��ޤ���';
  &error($err_log);
}
if ($user_name eq "") {
  $err_log = "[̾��] �����Ϥ���Ƥ��ޤ���";
  &error($err_log);
}
if ($u_mail_ad eq "") {
  $err_log = "[�᡼�륢�ɥ쥹] �����Ϥ���Ƥ��ޤ���";
  &error($err_log);
}

#####
# ��������ǧ����

# ����̵����

$maker_name =~ s/</&lt;/g;
$maker_name =~ s/>/&gt;/g;
$maker_name2 =~ s/</&lt;/g;
$maker_name2 =~ s/>/&gt;/g;
$url =~ s/</&lt;/g;
$url =~ s/>/&gt;/g;
$b_url =~ s/</&lt;/g;
$b_url =~ s/>/&gt;/g;
$width =~ s/</&lt;/g;
$width =~ s/>/&gt;/g;
$height =~ s/</&lt;/g;
$height =~ s/>/&gt;/g;
$comment =~ s/</&lt;/g;
$comment =~ s/>/&gt;/g;
$user_name =~ s/</&lt;/g;
$user_name =~ s/>/&gt;/g;
$u_mail_ad =~ s/</&lt;/g;
$u_mail_ad =~ s/>/&gt;/g;

# ���ԥ����ɤ� <br> ���Ѵ�
$comment_tmp = $comment;
$comment_tmp =~ s/\r\n/\n/g;
$comment_tmp =~ s/\n/<br>��/g;

print << "END_OF_HTML";
Content-type: text/html

<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=EUC-JP">
<title>�������ҥ�󥯽�(�������Ƴ�ǧ)</title>
<link rel="stylesheet" href="../../css/basecss.css" type="text/css">
</head>
<body>
<center><font color="#008000" size="6">�������Ƴ�ǧ</font><br></center>
�������ƤǤ������С���Ͽ�פ򡢽���������ϡ����פ򥯥�å����Ƥ���������<br><br>
�����Ծ���$who <br>
�᡼����/�֥���̾��$maker_name <br>
�եꥬ�ʡ�$maker_name2 <br>
URL��$url <br>
�Хʡ�URL��$b_url <br>
�Хʡ�������$width <br>
�Хʡ��⤵��$height <br>
����¾��<br>
&#x3000;$comment_tmp <br>
�����Ԥξ���<br>
&#x3000;̾����$user_name <br>
&#x3000;�᡼�륢�ɥ쥹��$u_mail_ad <br>

<!--
# mail.cgi �إǡ������Ϥ�
-->

<form method="post" action="mail.cgi">
<input type="hidden" name="who" value="$who"><p>
<input type="hidden" name="maker_name" value="$maker_name"><p>
<input type="hidden" name="maker_name2" value="$maker_name2"><p>
<input type="hidden" name="url" value="$url"><p>
<input type="hidden" name="b_url" value="$b_url"><p>
<input type="hidden" name="width" value="$width"><p>
<input type="hidden" name="height" value="$height"><p>
<input type="hidden" name="comment" value="$comment"><p>
<input type="hidden" name="user_name" value="$user_name"><p>
<input type="hidden" name="u_mail_ad" value="$u_mail_ad"><p>
<input type="submit" value="��Ͽ"><input LANGUAGE="JavaScript" type="button" value="���" onclick="history.back()" name="BACK">
</form>

<hr>

</body>
</html>
END_OF_HTML

exit(0);
