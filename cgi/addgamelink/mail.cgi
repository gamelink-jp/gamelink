#!/usr/bin/perl

require "./error.pl";
require "./data.pl";
require "./jcode.pl";

#####
# メール設定
$mailer = '/usr/lib/sendmail';
$g_mail_ad = 'addgamelink@gamelink.jp'; # ゲーム会社リンク集メールアドレス

#####
# error 処理

if ($ENV{'REQUEST_METHOD'} eq "POST") {
  if ($ENV{'CONTENT_LENGTH'} > 5000) {
    $err_log = "投稿量が大きすぎます。";
    &error($err_log);
  }
} else {
  $err_log = "このファイルは直接実行する事はできません。";
  &error($err_log);
}

#####
# formからデータ取得

&get_data();

#####
# ユーザーへメール送信

# subject作成
$mail_subject = 'ゲーム会社リンク集リンク追加依頼受付';

# スペース挿入
$comment_tmp = $comment;
$comment_tmp =~ s/\n/\n /g;

# mail 本文作成
$mail_body = <<"BODY";
下記内容で、ゲーム会社リンク集へのリンク追加依頼を受け付けました。
折り返しご連絡をさせて頂きますのでお待ちください。

記入者情報：$who
メーカー/ブランド名：$maker_name
フリガナ：$maker_name2
URL：$url
バナーURL：$b_url
バナー横幅：$width
バナー高さ：$height
その他：
 $comment_tmp
記入者の情報
 名前：$user_name
 メールアドレス：$u_mail_ad
BODY

# メール送信
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
  $error = 'メール送信エラー2';
  &error($err_log);
}

#####
# ゲーム会社リンク集へメール送信

# メーカー/ブランド名にフリガナを付加
if ($maker_name2 ne "") {
  $maker_name .= '(' . $maker_name2 . ')';
}

# subject作成
$mail_subject = 'ゲーム会社追加依頼';
$mail_subject .= '(' . $maker_name . ')'; # メーカー/ブランド名を付加

# 無記入の項目にデフォルト値を設定
if ($b_url eq "") {
  $b_url = '../png/nobanner.png';
}

if ($width eq "") {
  $width = 200;
}

if ($height eq "") {
  $height = 40;
}

# mail 本文作成
$mail_body = <<"BODY";
    <tr>
      <td class="banner"><a href="$url" target="_blank">
       <img src="$b_url" border="1" alt="banner" width="$width" height="$height"></a></td>
      <td><a href="$url" target="_blank">$maker_name</a></td>
    </tr>

<p><a href="$url" target="_blank">$maker_name</a></p>

$comment

記入者の情報
 名前：$user_name($who)
 メールアドレス：$u_mail_ad
BODY

# メール送信
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
  $error = 'メール送信エラー1';
  &error($err_log);
}

#####
# 結果表示

jcode'convert(*mail_header, "euc");
jcode'convert(*mail_body, "euc");
print << "END_OF_HTML";
Content-type: text/html

<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=EUC-JP">
<title>ゲーム会社リンク集(登録完了)</title>
<link rel="stylesheet" href="../../css/basecss.css" type="text/css">
</head>
<body>
登録依頼を受け付けました。ありがとうございます。<br>
折り返し管理者よりご連絡させていただきますのでお待ちください。<br>
<hr>
<a href="index.html">更にゲームメーカー/ブランドを登録する</a><br>
<a href="http://www.gamelink.jp/" target="main">戻る</a><br>
</body>
</html>
END_OF_HTML

exit(0);
