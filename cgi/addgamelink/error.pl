#!/usr/bin/perl

#####
# error 処理
sub error {
  my $err_log = shift;

  print  "Content-type: text/html\n\n";
print <<"HTML";
<html>
<head><title>ゲーム会社リンク集(CGIエラー)</title>
<link rel="stylesheet" href="../../css/basecss.css" type="text/css">
</head>
<body>
<font color="red">$err_log</font>
<hr>
<form method="post">
<input LANGUAGE="JavaScript" type="button" value="戻る" onclick="history.back()" name="BACK">
</form>
</body>
</html>
HTML

  exit(0);
}

1;
