#!/usr/bin/perl

#####
# error ����
sub error {
  my $err_log = shift;

  print  "Content-type: text/html\n\n";
print <<"HTML";
<html>
<head><title>�������ҥ�󥯽�(CGI���顼)</title>
<link rel="stylesheet" href="../../css/basecss.css" type="text/css">
</head>
<body>
<font color="red">$err_log</font>
<hr>
<form method="post">
<input LANGUAGE="JavaScript" type="button" value="���" onclick="history.back()" name="BACK">
</form>
</body>
</html>
HTML

  exit(0);
}

1;
