#!/usr/bin/perl

require "./error.pl";
require "./data.pl";
require "./jcode.pl";

#####
# �᡼������
$mailer = '/usr/lib/sendmail';
$g_mail_ad = 'addgamelink@gamelink.jp'; # �������ҥ�󥯽��᡼�륢�ɥ쥹

#####
# error ����

if ($ENV{'REQUEST_METHOD'} eq "POST") {
  if ($ENV{'CONTENT_LENGTH'} > 5000) {
    $err_log = "����̤��礭�����ޤ���";
    &error($err_log);
  }
} else {
  $err_log = "���Υե������ľ�ܼ¹Ԥ�����ϤǤ��ޤ���";
  &error($err_log);
}

#####
# form����ǡ�������

&get_data();

#####
# �桼�����إ᡼������

# subject����
$mail_subject = '�������ҥ�󥯽�����ɲð������';

# ���ڡ�������
$comment_tmp = $comment;
$comment_tmp =~ s/\n/\n /g;

# mail ��ʸ����
$mail_body = <<"BODY";
�������Ƥǡ��������ҥ�󥯽��ؤΥ���ɲð��������դ��ޤ�����
�ޤ��֤���Ϣ��򤵤���ĺ���ޤ��ΤǤ��Ԥ�����������

�����Ծ���$who
�᡼����/�֥���̾��$maker_name
�եꥬ�ʡ�$maker_name2
URL��$url
�Хʡ�URL��$b_url
�Хʡ�������$width
�Хʡ��⤵��$height
����¾��
 $comment_tmp
�����Ԥξ���
 ̾����$user_name
 �᡼�륢�ɥ쥹��$u_mail_ad
BODY

# �᡼������
jcode'convert(*mail_subject, "jis");
jcode'convert(*mail_body, "jis");
$mail_header = "From: $g_mail_ad\n";
$mail_header .= "To: $u_mail_ad\n";
$mail_header .= "Subject: $mail_subject\n\n";
$err = 0;
open(MAIL, "| $mailer -t -f'$g_mail_ad'") or $err = 1;
if ($err == 0) {
  print MAIL $mail_header;
  print MAIL $mail_body;
  print MAIL "\n";
  print MAIL "\n\n" . "." . "\n";
  close(MAIL);
} else {
  $error = '�᡼���������顼2';
  &error($err_log);
}

#####
# �������ҥ�󥯽��إ᡼������

# �᡼����/�֥���̾�˥եꥬ�ʤ��ղ�
if ($maker_name2 ne "") {
  $maker_name .= '(' . $maker_name2 . ')';
}

# subject����
$mail_subject = '���������ɲð���';
$mail_subject .= '(' . $maker_name . ')'; # �᡼����/�֥���̾���ղ�

# ̵�����ι��ܤ˥ǥե�����ͤ�����
if ($b_url eq "") {
  $b_url = '../png/nobanner.png';
}

if ($width eq "") {
  $width = 200;
}

if ($height eq "") {
  $height = 40;
}

# mail ��ʸ����
$mail_body = <<"BODY";
    <tr>
      <td class="banner"><a href="$url" target="_blank">
       <img src="$b_url" border="1" alt="banner" width="$width" height="$height"></a></td>
      <td><a href="$url" target="_blank">$maker_name</a></td>
    </tr>

<p><a href="$url" target="_blank">$maker_name</a></p>

$comment

�����Ԥξ���
 ̾����$user_name($who)
 �᡼�륢�ɥ쥹��$u_mail_ad
BODY

# �᡼������
jcode'convert(*mail_subject, "jis");
jcode'convert(*mail_body, "jis");
$mail_header = "From: $u_mail_ad\n";
$mail_header .= "To: $g_mail_ad\n";
$mail_header .= "Subject: $mail_subject\n\n";
$err = 0;
open(MAIL, "| $mailer -t -f'$u_mail_ad'") or $err = 1;
if ($err == 0) {
  print MAIL $mail_header;
  print MAIL $mail_body;
  print MAIL "\n";
  print MAIL "\n\n" . "." . "\n";
  close(MAIL);
} else {
  $error = '�᡼���������顼1';
  &error($err_log);
}

#####
# ���ɽ��

jcode'convert(*mail_header, "euc");
jcode'convert(*mail_body, "euc");
print << "END_OF_HTML";
Content-type: text/html

<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=EUC-JP">
<title>�������ҥ�󥯽�(��Ͽ��λ)</title>
<link rel="stylesheet" href="../../css/basecss.css" type="text/css">
</head>
<body>
��Ͽ���������դ��ޤ��������꤬�Ȥ��������ޤ���<br>
�ޤ��֤������Ԥ�ꤴϢ�����Ƥ��������ޤ��ΤǤ��Ԥ�����������<br>
<hr>
<a href="index.html">���˥�����᡼����/�֥��ɤ���Ͽ����</a><br>
<a href="http://www.gamelink.jp/" target="main">���</a><br>
</body>
</html>
END_OF_HTML

exit(0);
