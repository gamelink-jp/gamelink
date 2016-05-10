#!/usr/bin/perl

require "./error.pl";
require "./data.pl";
require "./jcode.pl";

#####
# error 処理

if ($ENV{'REQUEST_METHOD'} eq "POST") {
  if ($ENV{'CONTENT_LENGTH'} > 5000) {
    $err_log = '投稿量が大きすぎます。';
    &error($err_log);
  }
} else {
  $err_log = 'このファイルは直接実行する事はできません。';
  &error($err_log);
}

#####
# formからデータ取得

&get_data();

# 全角を半角に変換
$from = '−．：＿／〜＠０-９Ａ-Ｚａ-ｚ';
$to   = '-.:_/~@0-9A-Za-z';
&jcode'tr(*maker_name, $from, $to);
&jcode'tr(*url, $from, $to);
&jcode'tr(*b_url, $from, $to);
&jcode'tr(*width, $from, $to);
&jcode'tr(*height, $from, $to);
&jcode'tr(*u_mail_ad, $from, $to);

# 半角カナを全角カナに変換
&jcode'h2z_euc(*maker_name);
&jcode'h2z_euc(*maker_name2);
&jcode'h2z_euc(*comment);
&jcode'h2z_euc(*user_name);

#####
# 必須入力項目確認
if ($who eq "") {
  $err_log = '[記入者情報]が入力されていません。';
  &error($err_log);
}
if ($maker_name eq "") {
  $err_log = '[メーカー/ブランド名] が入力されていません。';
  &error($err_log);
}
if ($url eq "") {
  $err_log = '[URL] が入力されていません。';
  &error($err_log);
}
if ($user_name eq "") {
  $err_log = "[名前] が入力されていません。";
  &error($err_log);
}
if ($u_mail_ad eq "") {
  $err_log = "[メールアドレス] が入力されていません。";
  &error($err_log);
}

#####
# 送信前確認画面

# タグ無効化

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

# 改行コードを <br> に変換
$comment_tmp = $comment;
$comment_tmp =~ s/\r\n/\n/g;
$comment_tmp =~ s/\n/<br>　/g;

print << "END_OF_HTML";
Content-type: text/html

<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=EUC-JP">
<title>ゲーム会社リンク集(入力内容確認)</title>
<link rel="stylesheet" href="../../css/basecss.css" type="text/css">
</head>
<body>
<center><font color="#008000" size="6">入力内容確認</font><br></center>
この内容でよろしければ「登録」を、修正する場合は「戻る」をクリックしてください。<br><br>
記入者情報：$who <br>
メーカー/ブランド名：$maker_name <br>
フリガナ：$maker_name2 <br>
URL：$url <br>
バナーURL：$b_url <br>
バナー横幅：$width <br>
バナー高さ：$height <br>
その他：<br>
&#x3000;$comment_tmp <br>
記入者の情報<br>
&#x3000;名前：$user_name <br>
&#x3000;メールアドレス：$u_mail_ad <br>

<!--
# mail.cgi へデータを渡す
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
<input type="submit" value="登録"><input LANGUAGE="JavaScript" type="button" value="戻る" onclick="history.back()" name="BACK">
</form>

<hr>

</body>
</html>
END_OF_HTML

exit(0);
