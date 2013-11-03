#!/usr/bin/perl -w
# written by andrewt@cse.unsw.edu.au October 2013
# as a starting point for COMP2041 assignment 2
# http://www.cse.unsw.edu.au/~cs2041/assignments/mekong/

use CGI qw/:all/;
#use Mail::Sendmail;

$debug = 0;
$| = 1;

if (!@ARGV) {
	# run as a CGI script
	cgi_main();
	
} else {
	# for debugging purposes run from the command line
	console_main();
}
exit 0;

# This is very simple CGI code that goes straight
# to the search screen and it doesn't format the
# search results at all

# This is very simple CGI code that goes straight
# to the search screen and it doesn't format the
# search results at all

sub cgi_main {
	print page_header();
	print $ENV{"SCRIPT_URI"};
	
	set_global_variables();
	read_books($books_file);

	my $login = param('login');
	my $search_terms = param('search_terms');
	my $action = param('action');
	@paramKeys=(param());
	foreach (@paramKeys)
	{
		if(/action [a-zA-Z0-9]*/)
		{
			$detail=$_;
		}
	}
	#print $detail;
	
	if (defined $action) {
		print "action";
		print param("login")," ";
		print param("password")," ";
		if($action eq "Check out" && authenticate(param("login"),param("password"))) {
			print "Checkout";
			if (!read_basket($login))
			{
				print search_form(param("login"),param("password"),param("screen"));
				print print_user_button(param("login"),param("password"),param("screen"));
			}
			else
			{
				print basket_page(param("login"),param("password"),param("screen"),read_basket($login));
				print checkout_page($login);
			}
			
			
		} elsif($action eq "Finalize Order" && authenticate(param("login"),param("password"))) {
			print "Finalize Order";
			
			my ($credit_card_number, $expiry_date);
			$credit_card_number=param("credit_card_number");
			$expiry_date=param("expiry_date");
			$credit_card_number =~ s/\s//g;
			$expiry_date =~ s/\s//g;
			
			if($credit_card_number && $credit_card_number =~ /^\d{16}$/ && legal_credit_card_number($credit_card_number))
			{
				if($expiry_date && legal_expiry_date($expiry_date))
				{
					finalize_order($login, $credit_card_number, $expiry_date);
					print search_form(param("login"),param("password"),param("screen"));
					print print_user_button(param("login"),param("password"),param("screen"));
				}
				else
				{
					print "Invalid Expiry Date";
				}
			}
			else
			{
				print "Invalid Credit Card";
			}
			
		
			
			
			
			
			
		} elsif($action eq "Basket" && authenticate(param("login"),param("password"))) {
			print "Basket";
			print search_form(param("login"),param("password"),param("screen"));
			print basket_page(param("login"),param("password"),param("screen"),read_basket($login));
			print basket_user_button(param("login"),param("password"),param("screen"));
			#Need print total cost!!
		
		} elsif($action eq "View orders" && authenticate(param("login"),param("password"))) {
			print "View orders";
			
			order_page(param("login"),param("password"),param("screen"));
			print print_orders_button(param("login"),param("password"),param("screen"));
			
			#open(F,"<","$orders_dir/$login");
			#my @file=<F>;
			#print @file;
			#close F;
			#print "<br>";
			
			#foreach $ordNum(@file)
			#{
			#	$retOrder="";
			#	chomp($ordNum);
			#	$retOrder.=<<eof;
			#	<table bgcolor="white" border="1" align="center"><caption>Order #$ordNum - Thu Oct 31 20:02:57 2013<br>Credit Card Number: 1234567890123456 (Expiry 12/33)</caption>
			#	 <tr><td><img src="http://ecx.images-amazon.com/images/I/51i9Py7%2B88L._SL75_.jpg"></td> <td><i>Dogs: A New Understanding of Canine Origin, Behavior and Evolution</i><br>Raymond Coppinger
			#	Lorna Coppinger<br></td> <td align="right"><tt>price</tt></td> <td></td></tr>
			#	 <tr><td><b>Total</b></td> <td></td> <td align="right">totalPrice</td></tr>
			#	</table><p /><p />
#eof
#				print $retOrder;
#				open(F,"<","$orders_dir/$ordNum");
#				my @order=<F>;
#				print @order;
#				close F;
#				print "<br>";
#			}
			#ILOVEJACK
			#cat: ./orders/jack
			#read_basket($login)
		
		} elsif($action eq "Logout" && authenticate(param("login"),param("password"))) {
			print "Logout";
		
		} elsif($action eq "Create New Account") {
			print "Create new account";
			print newAccount_form();
		} elsif($action eq "Create Account") {
			print "Create account";
			my $email = param("email");
			my $user = param("login");
			my $msg = "Please Activate your new account by clicking this link ".$ENV{"SCRIPT_URI"}."?action=activate&user=$user";
			`echo "$msg" |mail -s 'Please Activate your new account' -- $email`;
			createTempAccount(param('login'),param('password'),param('name'),param('street'),param('city'),param('state'),param('postcode'),param('email'));	
			print login_form();
		} elsif($action eq "activate") {
			createAccount(param('user'));
			print login_form();
		} elsif($action eq "Login" && authenticate(param("login"),param("password"))) {
			print "Login Search";
			print search_form(param("login"),param("password"),param("screen"));
			print print_user_button(param("login"),param("password"),param("screen"));
		}
		elsif($action eq "Forget Password")
		{
			print forget_password_form();
		}
		elsif($action eq "Send Email")
		{
			print "Please Check your email to reset password.";
			
			#print <pre>`env`;
			#%mail = ( smtp => 'smtp.cse.unsw.edu.au',
			#		  To => 'hljw4@hotmail.com',
			#		  From => 'jwli898@cse.unsw.edu.au',
			#		  Message => 'Please click on this link'
			 #);

			#`sendmail(%mail)`;# or die $Mail::Sendmail::error;
			$username=param("username");
			$email='';
			open(F,'<',"$users_dir/$username");
			while(<F>)
			{
				if($_ =~ /email/)
				{
					$_ =~ s/.*=//;
					$email=$_;
				}
			}
			close F;
			$msg="Please click on this link ".$ENV{"SCRIPT_URI"}."?action=Reset&user=$username&email=$email";
			`echo "$msg" |mail -s 'Mekong password recovery' -- $email`;
		}
		elsif($action eq "Reset")
		{
			$username=param("user");
			$email=param("email");
			print reset_password_form($username,$email);
		}
		elsif($action eq "Reset Password")
		{
			$newPass=param("newPass");
			$username=param("user");
			$email=param("email");
			$email =~ tr/[A-Z]/[a-z]/;
			open(F,'<',"$users_dir/$username");
			$changePass=0;
			while(<F>)
			{
				if(/email/)
				{
					s/.*=//g;
					tr/[A-Z]/[a-z]/;
					chomp;
					print $_;
					print $email;
					if($_ eq $email)
					{
						$changePass=1;
					}
				}	
			}
			close F;
			if($changePass)
			{
				print "hello";
				open(F,'<',"$users_dir/$username");
				@file=<F>;
				close F;
				foreach $line (@file)
				{
					if($line =~ /password/)
					{
						$line =~ s/password=.*/password=$newPass/g;
					}	
				}
			}
			open(F,'>',"$users_dir/$username");
			print F @file;
			close F;
			print " loginform ";
			print login_form();
		}
		
		else
		{
			print " $last_error ";
			
			print " loginform ";
			print login_form();
		}
		
		
	#no action
	} elsif (defined $detail && $detail =~ /action [0-9]*/) {
		($action,$isbn)=split(' ',$detail);
		#print param($detail);
		if(param($detail) eq "Add"){
			print "addBasket";
			add_basket($login,$isbn);
			#print hidden_inputs(param("login"),param("password"),param("screen"));
			if(param("screen") eq "Details")
			{
				print detail_page($isbn);
				print details_user_button(param("login"),param("password"),param("screen"),$detail);
				review_page($isbn);
			}
			else
			{
				print search_results(param("login"),param("password"),param("screen"),$search_terms);
				print print_user_button(param("login"),param("password"),param("screen"));
			}
			
		}
		elsif(param($detail) eq "Drop")
		{
			print "deleteBasket";
			delete_basket($login,$isbn);
			print basket_page(param("login"),param("password"),param("screen"),read_basket($login));
		}
		elsif(param($detail) eq "Post Review")
		{	
			#post review
			print "Post Review";
			write_review(param("login"),param("Review"),$isbn);
			print detail_page($isbn);
			print details_user_button(param("login"),param("password"),param("screen"),$detail);
			review_page($isbn);
		}
		else{ # details
			print "Detail";
			print detail_page($isbn);
			print details_user_button(param("login"),param("password"),param("screen"),$detail);
			print review_page($isbn);
		}
	
	} elsif (defined $search_terms) {
			print "search terms";
			param(-name=>'screen',-value=>'searchRes');
			print search_results(param("login"),param("password"),param("screen"),$search_terms);
			print print_user_button(param("login"),param("password"),param("screen"));
		#}
	} else {
		
		print "loginform";
		print login_form();
	}
	
	print page_trailer();
}

# simple login form without authentication	
sub login_form {
	#create reviews file
	if(!(-e "$base_dir/reviews")) 
	{
		open(F,'>',"$base_dir/reviews");
		close F;
	}

	return <<eof;
	<p>
	<form method="post" action="$ENV{"SCRIPT_URI"}" enctype="multipart/form-data">
		<input type="hidden" name="screen" value="search">
		<table align="center">
		<tr><td>login: </td><td><input type="text" name="login" size=16></input></td></tr>
		<tr><td>password: </td> <td><input type="password" name="password" size=16></input></td></tr>
		
		<tr><td align="center" colspan="2"> 
		<input class="btn" type="submit" name="action" value="Login">
		<input class="btn" type="submit" name="action" value="Create New Account">
		<input class="btn" type="submit" name="action" value="Forget Password">
		</td></tr>
		</table>
		
	</form>
	<p>
eof
}

sub forget_password_form {
	return <<eof;
	<div align="center">
	<form method="post" action="$ENV{"SCRIPT_URI"}" enctype="multipart/form-data">
		<input type="text" name="username" placeholder="Username" size=60></input><br>
		<input class="btn" type="submit" name="action" value="Send Email">
	</form>
	</div>
eof
}

sub reset_password_form {
	my($username,$email)=@_;
	return <<eof;
	<div align="center">
	<form method="post" action="$ENV{"SCRIPT_URI"}" enctype="multipart/form-data">
		<input type="hidden" name="user" value="$username">
		<input type="hidden" name="email" value="$email">
		<input type="text" name="newPass" placeholder="New Password" size=60></input><br>
		<input class="btn" type="submit" name="action" value="Reset Password">
	</form>
	</div>
eof
}

sub hidden_inputs {
	my ($login,$password,$screen)=@_;
	return <<eof;
	<input type="hidden" name="screen" value="$screen">
	<input type="hidden" name="login" value="$login">
	<input type="hidden" name="password" value="$password">
eof
}
sub newAccount_form {
	return <<eof;
	<form method="post" action="$ENV{"SCRIPT_URI"}" enctype="multipart/form-data">
	<input type="hidden" name="screen" value="new_account"><p /><p />
	<table align="center"><caption><font color=red></font></caption> <tr><td>Login:</td> <td><input type="text" name="login"  width="10" /></td></tr>
	 <tr><td>Password:</td> <td><input type="password" name="password"  width="10" /></td></tr>
	 <tr><td>Full Name:</td> <td><input type="text" name="name"  width="50" /></td></tr>
	 <tr><td>Street:</td> <td><input type="text" name="street"  width="50" /></td></tr>
	 <tr><td>City/Suburb:</td> <td><input type="text" name="city"  width="25" /></td></tr>
	 <tr><td>State:</td> <td><input type="text" name="state"  width="25" /></td></tr>
	 <tr><td>Postcode:</td> <td><input type="text" name="postcode"  width="25" /></td></tr>
	 <tr><td>Email Address:</td> <td><input type="text" name="email"  width="35" /></td></tr>
	 <tr><td align="center" colspan="1"> <input class="btn" type="submit" name="action" value="Create Account">
	</td></tr>
	</table>
	</form>
eof
}

#create 
sub createTempAccount {
	my ($login,$password,$name,$street,$city,$state,$postcode,$email) = @_;
	open (F,">$users_dir/temp_$login");
	
	#`touch /users/temp_$login`;
	#`print to file`
	print F "password=$password\n";
	print F "name=$name\n";
	print F "street=$street\n";
	print F "city=$city\n";
	print F "state=$state\n";
	print F "postcode=$postcode\n";
	print F "email=$email\n";
	
	close F;
}

sub createAccount {
	my ($login)= @_;
	`mv "$users_dir/temp_$login" "$users_dir/$login"`;
}

# simple search form
sub search_form {
	my($login,$password,$screen)=@_;
	my $ret.=<<eof;
	<p>
	<form method="post" action="$ENV{"SCRIPT_URI"}" enctype="multipart/form-data">
eof
	$ret.=hidden_inputs(param("login"),param("password"),param("screen"));
	$ret.=<<eof;
	<table align="center"><tr><td align="center">
		search: <input type="text" name="search_terms" size=60></input>
	</td></tr></table>
	</form>
	<p>
	<!--Testing-->
eof
	return $ret;
}

#search
sub search_results {
	my ($login,$password,$screen,$search_terms) = @_;
	my $ret="";
	my @matching_isbns = search_books($search_terms);
	my $descriptions = get_book_descriptions_search(@matching_isbns);
	$ret.='<form method="post" action="'.$ENV{"SCRIPT_URI"}.'" enctype="multipart/form-data">';
	$ret.=hidden_inputs($login,$password,$screen);
	$ret.=<<eof;
	<!--<p>$search_terms-->
		<table align="center"><tr><td align="center">
			search: <input type="text" name="search_terms" value="$search_terms" size=60></input>
		</td></tr></table>
	<!--<p>@matching_isbns-->
	<!--<pre>-->
			<table bgcolor="white" border="1" align="center"><caption></caption>
			$descriptions
			</table>
	<!--</pre>-->
	<p>
	<!--NOT ME-->
	</form>
eof
	return $ret;
}
sub get_book_descriptions_search {
	my @isbns = @_;
	my $descriptions = "";
	our %book_details;
	foreach $isbn (@isbns) {
		die "Internal error: unknown isbn $isbn in print_books\n" if !$book_details{$isbn}; # shouldn't happen
		my $title = $book_details{$isbn}{title} || "";
		my $authors = $book_details{$isbn}{authors} || "";
		$authors =~ s/\n([^\n]*)$/ & $1/g;
		$authors =~ s/\n/, /g;
		$descriptions .= sprintf '<tr><td><img src="%s"></td> <td><i>%s</i><br>%s<br></td> <td align="right"><tt>%7s</tt></td> <td><input class="btn" type="submit" name="action '.$isbn.'" value="Add"><br>',$book_details{$isbn}{smallimageurl},$title,$authors,$book_details{$isbn}{price};
		$descriptions .= '<input class="btn" type="submit" name="action '.$isbn.'" value="Details"><br>';
		$descriptions .= '</td></tr>';
	}
	
	
	
	return $descriptions;
}

#detail
sub detail_page {
	my $isbn = $_[0];
	#print_books($isbn);
	our %book_details;
	$ret.=<<eof;
	<h2>$book_details{$isbn}{title} - $book_details{$isbn}{authors}</h2>
	<p>$book_details{$isbn}{productdescription}</p>
	<table bgcolor="white" align="center">
		<tr><td><img src="$book_details{$isbn}{largeimageurl}"></td></tr>
	</table>
	<table bgcolor="white" align="center">
	 <tr><td><b>authors</b></td> <td>Jake Page</td></tr>
	 <tr><td><b>binding</b></td> <td>Hardcover</td></tr>
	 <tr><td><b>catalog</b></td> <td>Book</td></tr>
	 <tr><td><b>ean</b></td> <td>9780061456480</td></tr>
	 <tr><td><b>edition</b></td> <td>1</td></tr>
	 <tr><td><b>isbn</b></td> <td>0061456489</td></tr>
	 <tr><td><b>numpages</b></td> <td>224</td></tr>
	 <tr><td><b>price</b></td> <td>\$24.95</td></tr>
	 <tr><td><b>publication_date</b></td> <td>2008-11-18</td></tr>
	 <tr><td><b>publisher</b></td> <td>Smithsonian</td></tr>
	 <tr><td><b>releasedate</b></td> <td>2008-11-18</td></tr>
	 <tr><td><b>salesrank</b></td> <td>1349717</td></tr>
	 <tr><td><b>title</b></td> <td>Do Cats Hear with Their Feet?: Where Cats Come From, What We Know About Them, and What They Think About Us</td></tr>
	 <tr><td><b>year</b></td> <td>2008</td></tr>
	</table>
eof
	
	return $ret;
}

sub review_page {
	my ($isbn) = @_;
	open(F,"+<","$base_dir/reviews");
	print '<div align="center">';
	print '<b>Reviews</b>';
	print '</div><br>';
	my $foundBook=0;
	while(<F>)
	{	
		if($foundBook==0)
		{
			if(/$isbn/)
			{
				$foundBook=1;
			}
		}
		else
		{
			if(/$isbn/)
			{
				last;
			}
			else
			{
				print '<div align="center">';
				print $_;
				print '</div>';
			}
		}
	}
	close F;
}

sub write_review {
	my ($login,$review,$isbn) = @_;
	print $isbn;
	open(F,"<","$base_dir/reviews");
	open(FOUT,">","$base_dir/reviews.temp");
	$found=0;
	while(<F>)
	{
		if(/.*$isbn:$/)
		{
			print FOUT $_;
			print FOUT "$review by $login\n";
			$found=1;
		}
		elsif(/.*$isbn:end$/)
		{
			print FOUT $_;
			last;
		}
		else
		{
			print FOUT $_;
		}
	}
	close FOUT;
	close F;
	
	if(!$found)
	{
		open(FOUT,">>","$base_dir/reviews.temp");
		print FOUT "$isbn:\n";
		print FOUT "$review by $login\n";
		print FOUT "$isbn:end\n";
		close FOUT;
	}
	`rm $base_dir/reviews`;
	`mv $base_dir/reviews.temp $base_dir/reviews`;
}

#basket
sub basket_page {
	my($login,$password,$screen,@isbns)=@_;
	if(@isbns==0)
	{
		return <<eof;
		<table bgcolor="white" align="center">
		<tr><td>You have nothing!</td></tr>
		</table>
		<br>
eof
	}
	my ($descriptions,$total) = get_book_descriptions_basket($login,$password,$screen,@isbns);
	return <<eof;
	<!--<pre>-->
		<table bgcolor="white" border="1" align="center"><caption></caption>
		$descriptions
		<tr><td><b>Total</b></td> <td></td> <td align="right">$total</td></tr>
		</table>
	<!--</pre>-->
	<p>
eof
}


sub get_book_descriptions_basket {
	my($login,$password,$screen,@isbns)=@_;
	my $descriptions = "";
	our %book_details;
	my $sum=0;
	$descriptions.='<form method="post" action="'.$ENV{"SCRIPT_URI"}.'" enctype="multipart/form-data">';
	$descriptions.=hidden_inputs($login,$password,$screen);
	foreach $isbn (@isbns) {
		if (!$book_details{$isbn}) # shouldn't happen
		{
			#print "Internal error: unknown isbn $isbn in print_books\n" ;
			last;
		}
		my $title = $book_details{$isbn}{title} || "";
		my $authors = $book_details{$isbn}{authors} || "";
		$authors =~ s/\n([^\n]*)$/ & $1/g;
		$authors =~ s/\n/, /g;
		$descriptions .= sprintf '<tr><td><img src="%s"></td> <td><i>%s</i><br>%s<br></td> <td align="right"><tt>%7s</tt></td> <td><input class="btn" type="submit" name="action '.$isbn.'" value="Drop"><br>',$book_details{$isbn}{smallimageurl},$title,$authors,$book_details{$isbn}{price};
		$descriptions .= '<input class="btn" type="submit" name="action '.$isbn.'" value="Details"><br>';
		$descriptions .= '</td></tr>';
		my $price=$book_details{$isbn}{price};
		$price =~ s/\$//g;
		$sum+=$price;
	}
	$descriptions.='</form>';
	
	return ($descriptions,'$'.$sum);
}

#check out
sub checkout_page {
	my ($login) = @_;
	my @basket_isbns = read_basket($login);
	$ret="";
	if (!@basket_isbns) {
		$ret.="Your shopping basket is empty.\n";
		return $ret;
	}
	$ret.=<<eof;
	<b>Shipping Details:</b><pre>\n$user_details{name},\n$user_details{street},\n$user_details{city},\n$user_details{state}, \n$user_details{postcode}\n</pre>
eof
	$ret.='<form method="post" action="$ENV{"SCRIPT_URI"}" enctype="multipart/form-data">';
	$ret.=hidden_inputs(param("login"),param("password"),param("screen"));
	$ret.=<<eof;
		<p /><table align="center"><caption><font color=red></font></caption> <tr><td>Credit Card Number:</td> <td><input type="text" name="credit_card_number"  width="16" /></td></tr>
		 <tr><td>Expiry date (mm/yy):</td> <td><input type="text" name="expiry_date"  width="5" /></td></tr>
		 <tr><td align="center" colspan="4"> <input class="btn" type="submit" name="action" value="Basket">
		  <input class="btn" type="submit" name="action" value="Finalize Order">
		  <input class="btn" type="submit" name="action" value="View orders">
		  <input class="btn" type="submit" name="action" value="Logout">
		</td></tr></table>
	</form>
eof
	return $ret;
	
	print_books(@basket_isbns);
	printf "Total: %11s\n", sprintf("\$%.2f", total_books(@basket_isbns));
	print "\n";
	my ($credit_card_number, $expiry_date);
	while (1) {
			print "Credit Card Number: ";
			$credit_card_number = <>;
			exit 1 if !$credit_card_number;
			$credit_card_number =~ s/\s//g;
			next if !$credit_card_number;
			last if $credit_card_number =~ /^\d{16}$/;
			last if legal_credit_card_number($credit_card_number);
			print "$last_error\n";
	}
	while (1) {
			print "Expiry date (mm/yy): ";
			$expiry_date = <>;
			exit 1 if !$expiry_date;
			$expiry_date =~ s/\s//g;
			next if !$expiry_date;
			last if legal_expiry_date($expiry_date);
			print "$last_error\n";
	}
	finalize_order($login, $credit_card_number, $expiry_date);
}

#View orders
sub order_page {
	my($login,$password,$screen)=@_;
	print "\n";
	my $ret="";
	foreach $order (login_to_orders($login)) {
		my ($order_time, $credit_card_number, $expiry_date, @isbns) = read_order($order);
		$order_time = localtime($order_time);
		$ret="";
		$ret.=<<eof;
		<table bgcolor="white" align="center">
		<tr><td align="center">Order #$order - $order_time</td></tr>
		<tr><td align="center">Credit Card Number: $credit_card_number (Expiry $expiry_date)</td></tr>
		</table>
eof
		$ret.=basket_page(param("login"),param("password"),param("screen"),@isbns);
		print $ret;
	}
}

sub print_orders_button {
	my($login,$password,$screen)=@_;
	$ret.=<<eof;
	<form method="post" action="$ENV{"SCRIPT_URI"}" enctype="multipart/form-data">
	<table align="center"><caption><font color=red></font></caption> <tr><td align="center" colspan="4"> 
eof
	$ret.=hidden_inputs($login,$password,$screen);
	$ret.=<<eof;
	<input class="btn" type="submit" name="action" value="Basket">
	<input class="btn" type="submit" name="action" value="Check out">
	<input class="btn" type="submit" name="action" value="Logout">
	</td></tr></table>
	</form>
eof
	return $ret;
}

sub print_user_button {
	my($login,$password,$screen)=@_;
	my $ret.=<<eof;
	<form method="post" action="$ENV{"SCRIPT_URI"}" enctype="multipart/form-data">
	<table align="center"><caption><font color=red></font></caption> <tr><td align="center" colspan="4"> 
eof
	$ret.=hidden_inputs($login,$password,$screen);
	$ret.=<<eof;
	<input class="btn" type="submit" name="action" value="Basket">
	<input class="btn" type="submit" name="action" value="Check out">
	<input class="btn" type="submit" name="action" value="View orders">
	<input class="btn" type="submit" name="action" value="Logout">
	</td></tr></table>
	</form>
eof
	return $ret;
}

sub details_user_button {
	my($login,$password,$screen,$detail)=@_;
	my $ret.=<<eof;


	<form method="post" action="$ENV{"SCRIPT_URI"}" enctype="multipart/form-data">

	<table align="center"><caption><font color=red></font></caption> <tr><td align="center" colspan="4">
eof
	$ret.=hidden_inputs($login,$password,"Details");
	$ret.=<<eof;
	<br>
	<textarea class="field" name="Review" value="" placeholder="Write your review here!"></textarea>
	<input class="btn" type="submit" name="$detail" value="Post Review">
	<br>
	<br>
	<input class="btn" type="submit" name="$detail" value="Add">
	<input class="btn" type="submit" name="action" value="Basket">
	<input class="btn" type="submit" name="action" value="Check out">
	<input class="btn" type="submit" name="action" value="Logout">
	</td></tr></table>
	</form>

	
eof
	return $ret;
}

sub basket_user_button {
	my($login,$password,$screen)=@_;
	my $ret.=<<eof;
	<form method="post" action="$ENV{"SCRIPT_URI"}" enctype="multipart/form-data">
	<table align="center"><caption><font color=red></font></caption> <tr><td align="center" colspan="4">
eof
	$ret.=hidden_inputs($login,$password,$screen);
	$ret.=<<eof;
	<input class="btn" type="submit" name="action" value="Check out">
	<input class="btn" type="submit" name="action" value="View orders">
	<input class="btn" type="submit" name="action" value="Logout">
	</td></tr></table>
	</form>
eof
	return $ret;
}

#
# HTML at top of every screen
#
sub page_header() {
	return <<eof;
Content-Type: text/html

<!DOCTYPE html>
<html lang="en">
<head>
<title>mekong.com.au</title>
<link href="//netdna.bootstrapcdn.com/twitter-bootstrap/2.3.1/css/bootstrap-combined.min.css" rel="stylesheet">
<script src="//netdna.bootstrapcdn.com/twitter-bootstrap/2.3.1/js/bootstrap.min.js"></script>
<script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.0.8/angular.min.js"></script>
<!-- AddThis Smart Layers BEGIN -->
<!-- Go to http://www.addthis.com/get/smart-layers to customize -->
<script type="text/javascript" src="//s7.addthis.com/js/300/addthis_widget.js#pubid=xa-52742d27315496a3"></script>
<script type="text/javascript">
  addthis.layers({
    'theme' : 'transparent',
    'share' : {
      'position' : 'right',
      'numPreferredServices' : 5
    },  
    'whatsnext' : {},  
    'recommended' : {} 
  });
</script>
<!-- AddThis Smart Layers END -->
</head>
<body>

<div ng-app>
	<form method="post" action="$ENV{"SCRIPT_URI"}" enctype="multipart/form-data" >
	<label>Name:</label>
		 <input type="text" name="yourName" ng-model="yourName" placeholder="Enter a name here">
		 <hr>
		 <h1>Hello {{yourName * 3}}!</h1>
		 </form>
		 </div>

<p>
<div class="container">
eof
}

#
# HTML at bottom of every screen
#
sub page_trailer() {
	my $debugging_info = debugging_info();
	
	return <<eof;
	$debugging_info
	</div>
<body>
</html>
eof
}

#
# Print out information for debugging purposes
#
sub debugging_info() {
	my $params = "";
	foreach $p (param()) {
		$params .= "param($p)=".param($p)."\n"
	}

	return <<eof;
<hr>
<h4>Debugging information - parameter values supplied to $0</h4>
<pre>
$params
</pre>
<hr>
eof
}




###
### Below here are utility functions
### Most are unused by the code above, but you will 
### need to use these functions (or write your own equivalent functions)
### 
###

# return true if specified string can be used as a login

sub legal_login {
	my ($login) = @_;
	our ($last_error);

	if ($login !~ /^[a-zA-Z][a-zA-Z0-9]*$/) {
		$last_error = "Invalid login '$login': logins must start with a letter and contain only letters and digits.";
		return 0;
	}
	if (length $login < 3 || length $login > 8) {
		$last_error = "Invalid login: logins must be 3-8 characters long.";
		return 0;
	}
	return 1;
}

# return true if specified string can be used as a password

sub legal_password {
	my ($password) = @_;
	our ($last_error);
	
	if ($password =~ /\s/) {
		$last_error = "Invalid password: password can not contain white space.";
		return 0;
	}
	if (length $password < 5) {
		$last_error = "Invalid password: passwords must contain at least 5 characters.";
		return 0;
	}
	return 1;
}


# return true if specified string could be an ISBN

sub legal_isbn {
	my ($isbn) = @_;
	our ($last_error);
	
	return 1 if $isbn =~ /^\d{9}(\d|X)$/;
	$last_error = "Invalid isbn '$isbn' : an isbn must be exactly 10 digits.";
	return 0;
}


# return true if specified string could be an credit card number

sub legal_credit_card_number {
	my ($number) = @_;
	our ($last_error);
	
	return 1 if $number =~ /^\d{16}$/;
	$last_error = "Invalid credit card number - must be 16 digits.\n";
	return 0;
}

# return true if specified string could be an credit card expiry date

sub legal_expiry_date {
	my ($expiry_date) = @_;
	our ($last_error);
	
	return 1 if $expiry_date =~ /^\d\d\/\d\d$/;
	$last_error = "Invalid expiry date - must be mm/yy, e.g. 11/04.\n";
	return 0;
}



# return total cost of specified books

sub total_books {
	my @isbns = @_;
	our %book_details;
	$total = 0;
	foreach $isbn (@isbns) {
		die "Internal error: unknown isbn $isbn  in total_books" if !$book_details{$isbn}; # shouldn't happen
		my $price = $book_details{$isbn}{price};
		$price =~ s/[^0-9\.]//g;
		$total += $price;
	}
	return $total;
}

# return true if specified login & password are correct
# user's details are stored in hash user_details

sub authenticate {
	my ($login, $password) = @_;
	our (%user_details, $last_error);
	
	return 0 if !legal_login($login);
	if (!open(USER, "$users_dir/$login")) {
		$last_error = "User '$login' does not exist.";
		return 0;
	}
	my %details =();
	while (<USER>) {
		next if !/^([^=]+)=(.*)/;
		$details{$1} = $2;
	}
	close(USER);
	foreach $field (qw(name street city state postcode password)) {
		if (!defined $details{$field}) {
 	 	 	$last_error = "Incomplete user file: field $field missing";
			return 0;
		}
	}
	if ($details{"password"} ne $password) {
  	 	$last_error = "Incorrect password.";
		return 0;
	 }
	 %user_details = %details;
  	 return 1;
}

# read contents of files in the books dir into the hash book
# a list of field names in the order specified in the file
 
sub read_books {
	my ($books_file) = @_;
	our %book_details;
	print STDERR "read_books($books_file)\n" if $debug;
	open BOOKS, $books_file or die "Can not open books file '$books_file'\n";
	my $isbn;
	while (<BOOKS>) {
		if (/^\s*"(\d+X?)"\s*:\s*{\s*$/) {
			$isbn = $1;
			next;
		}
		next if !$isbn;
		my ($field, $value);
		if (($field, $value) = /^\s*"([^"]+)"\s*:\s*"(.*)",?\s*$/) {
			$attribute_names{$field}++;
			print STDERR "$isbn $field-> $value\n" if $debug > 1;
			$value =~ s/([^\\]|^)\\"/$1"/g;
	  		$book_details{$isbn}{$field} = $value;
		} elsif (($field) = /^\s*"([^"]+)"\s*:\s*\[\s*$/) {
			$attribute_names{$1}++;
			my @a = ();
			while (<BOOKS>) {
				last if /^\s*\]\s*,?\s*$/;
				push @a, $1 if /^\s*"(.*)"\s*,?\s*$/;
			}
	  		$value = join("\n", @a);
			$value =~ s/([^\\]|^)\\"/$1"/g;
	  		$book_details{$isbn}{$field} = $value;
	  		print STDERR "book{$isbn}{$field}=@a\n" if $debug > 1;
		}
	}
	close BOOKS;
}

# return books matching search string

sub search_books {
	my ($search_string) = @_;
	$search_string =~ s/\s*$//;
	$search_string =~ s/^\s*//;
	return search_books1(split /\s+/, $search_string);
}

# return books matching search terms

sub search_books1 {
	my (@search_terms) = @_;
	our %book_details;
	print STDERR "search_books1(@search_terms)\n" if $debug;
	my @unknown_fields = ();
	foreach $search_term (@search_terms) {
		push @unknown_fields, "'$1'" if $search_term =~ /([^:]+):/ && !$attribute_names{$1};
	}
	printf STDERR "$0: warning unknown field%s: @unknown_fields\n", (@unknown_fields > 1 ? 's' : '') if @unknown_fields;
	my @matches = ();
	BOOK: foreach $isbn (sort keys %book_details) {
		my $n_matches = 0;
		if (!$book_details{$isbn}{'=default_search='}) {
			$book_details{$isbn}{'=default_search='} = ($book_details{$isbn}{title} || '')."\n".($book_details{$isbn}{authors} || '');
			print STDERR "$isbn default_search -> '".$book_details{$isbn}{'=default_search='}."'\n" if $debug;
		}
		print STDERR "search_terms=@search_terms\n" if $debug > 1;
		foreach $search_term (@search_terms) {
			my $search_type = "=default_search=";
			my $term = $search_term;
			if ($search_term =~ /([^:]+):(.*)/) {
				$search_type = $1;
				$term = $2;
			}
			print STDERR "term=$term\n" if $debug > 1;
			while ($term =~ s/<([^">]*)"[^"]*"([^>]*)>/<$1 $2>/g) {}
			$term =~ s/<[^>]+>/ /g;
			next if $term !~ /\w/;
			$term =~ s/^\W+//g;
			$term =~ s/\W+$//g;
			$term =~ s/[^\w\n]+/\\b +\\b/g;
			$term =~ s/^/\\b/g;
			$term =~ s/$/\\b/g;
			next BOOK if !defined $book_details{$isbn}{$search_type};
			print STDERR "search_type=$search_type term=$term book=$book_details{$isbn}{$search_type}\n" if $debug;
			my $match;
			eval {
				my $field = $book_details{$isbn}{$search_type};
				# remove text that looks like HTML tags (not perfect)
				while ($field =~ s/<([^">]*)"[^"]*"([^>]*)>/<$1 $2>/g) {}
				$field =~ s/<[^>]+>/ /g;
				$field =~ s/[^\w\n]+/ /g;
				$match = $field !~ /$term/i;
			};
			if ($@) {
				$last_error = $@;
				$last_error =~ s/;.*//;
				return (); 
			}
			next BOOK if $match;
			$n_matches++;
		}
		push @matches, $isbn if $n_matches > 0;
	}
	
	sub bySalesRank {
		my $max_sales_rank = 100000000;
		my $s1 = $book_details{$a}{SalesRank} || $max_sales_rank;
		my $s2 = $book_details{$b}{SalesRank} || $max_sales_rank;
		return $a cmp $b if $s1 == $s2;
		return $s1 <=> $s2;
	}
	
	return sort bySalesRank @matches;
}


# return books in specified user's basket

sub read_basket {
	my ($login) = @_;
	our %book_details;
	open F, "$baskets_dir/$login" or return ();
	my @isbns = <F>;

	close(F);
	chomp(@isbns);
	!$book_details{$_} && die "Internal error: unknown isbn $_ in basket\n" foreach @isbns;
	return @isbns;
}


# delete specified book from specified user's basket
# only first occurance is deleted

sub delete_basket {
	my ($login, $delete_isbn) = @_;
	my @isbns = read_basket($login);
	open F, ">$baskets_dir/$login" or die "Can not open $baskets_dir/$login: $!";
	foreach $isbn (@isbns) {
		if ($isbn eq $delete_isbn) {
			$delete_isbn = "";
			next;
		}
		print F "$isbn\n";
	}
	close(F);
	unlink "$baskets_dir/$login" if ! -s "$baskets_dir/$login";
}


# add specified book to specified user's basket

sub add_basket {
	my ($login, $isbn) = @_;
	open F, ">>$baskets_dir/$login" or die "Can not open $baskets_dir/$login::$! \n";
	print F "$isbn\n";
	close(F);
}


# finalize specified order

sub finalize_order {
	my ($login, $credit_card_number, $expiry_date) = @_;
	my $order_number = 0;

	if (open ORDER_NUMBER, "$orders_dir/NEXT_ORDER_NUMBER") {
		$order_number = <ORDER_NUMBER>;
		chomp $order_number;
		close(ORDER_NUMBER);
	}
	$order_number++ while -r "$orders_dir/$order_number";
	open F, ">$orders_dir/NEXT_ORDER_NUMBER" or die "Can not open $orders_dir/NEXT_ORDER_NUMBER: $!\n";
	print F ($order_number + 1);
	close(F);

	my @basket_isbns = read_basket($login);
	open ORDER,">$orders_dir/$order_number" or die "Can not open $orders_dir/$order_number:$! \n";
	print ORDER "order_time=".time()."\n";
	print ORDER "credit_card_number=$credit_card_number\n";
	print ORDER "expiry_date=$expiry_date\n";
	print ORDER join("\n",@basket_isbns)."\n";
	close(ORDER);
	unlink "$baskets_dir/$login";
	
	open F, ">>$orders_dir/$login" or die "Can not open $orders_dir/$login:$! \n";
	print F "$order_number\n";
	close(F);
	
}


# return order numbers for specified login

sub login_to_orders {
	my ($login) = @_;
	open F, "$orders_dir/$login" or return ();
	@order_numbers = <F>;
	close(F);
	chomp(@order_numbers);
	return @order_numbers;
}



# return contents of specified order

sub read_order {
	my ($order_number) = @_;
	open F, "$orders_dir/$order_number" or warn "Can not open $orders_dir/$order_number:$! \n";
	@lines = <F>;
	close(F);
	chomp @lines;
	foreach (@lines[0..2]) {s/.*=//};
	return @lines;
}

###
### functions below are only for testing from the command line
### Your do not need to use these funtions
###

sub console_main {
	set_global_variables();
	$debug = 1;
	foreach $dir ($orders_dir,$baskets_dir,$users_dir) {
		if (! -d $dir) {
			print "Creating $dir\n";
			mkdir($dir, 0777) or die("Can not create $dir: $!");
		}
	}
	read_books($books_file);
	my @commands = qw(login new_account search details add drop basket checkout orders quit);
	my @commands_without_arguments = qw(basket checkout orders quit);
	my $login = "";
	
	print "mekong.com.au - ASCII interface\n";
	while (1) {
		$last_error = "";
		print "> ";
		$line = <STDIN> || last;
		$line =~ s/^\s*>\s*//;
		$line =~ /^\s*(\S+)\s*(.*)/ || next;
		($command, $argument) = ($1, $2);
		$command =~ tr/A-Z/a-z/;
		$argument = "" if !defined $argument;
		$argument =~ s/\s*$//;
		
		if (
			$command !~ /^[a-z_]+$/ ||
			!grep(/^$command$/, @commands) ||
			grep(/^$command$/, @commands_without_arguments) != ($argument eq "") ||
			($argument =~ /\s/ && $command ne "search")
		) {
			chomp $line;
			$line =~ s/\s*$//;
			$line =~ s/^\s*//;
			incorrect_command_message("$line");
			next;
		}

		if ($command eq "quit") {
			print "Thanks for shopping at mekong.com.au.\n";
			last;
		}
		if ($command eq "login") {
			$login = login_command($argument);
			next;
		} elsif ($command eq "new_account") {
			$login = new_account_command($argument);
			next;
		} elsif ($command eq "search") {
			search_command($argument);
			next;
		} elsif ($command eq "details") {
			details_command($argument);
			next;
		}
		
		if (!$login) {
			print "Not logged in.\n";
			next;
		}
		
		if ($command eq "basket") {
			basket_command($login);
		} elsif ($command eq "add") {
			add_command($login, $argument);
		} elsif ($command eq "drop") {
			drop_command($login, $argument);
		} elsif ($command eq "checkout") {
			checkout_command($login);
		} elsif ($command eq "orders") {
			orders_command($login);
		} else {
			warn "internal error: unexpected command $command";
		}
	}
}

sub login_command {
	my ($login) = @_;
	if (!legal_login($login)) {
		print "$last_error\n";
		return "";
	}
	if (!-r "$users_dir/$login") {
		print "User '$login' does not exist.\n";
		return "";
	}
	printf "Enter password: ";
	my $pass = <STDIN>;
	chomp $pass;
	if (!authenticate($login, $pass)) {
		print "$last_error\n";
		return "";
	}
	$login = $login;
	print "Welcome to mekong.com.au, $login.\n";
	return $login;
}

sub new_account_command {
	my ($login) = @_;
	if (!legal_login($login)) {
		print "$last_error\n";
		return "";
	}
	if (-r "$users_dir/$login") {
		print "Invalid user name: login already exists.\n";
		return "";
	}
	if (!open(USER, ">$users_dir/$login")) {
		print "Can not create user file $users_dir/$login: $!";
		return "";
	}
	foreach $description (@new_account_rows) {
		my ($name, $label)  = split /\|/, $description;
		next if $name eq "login";
		my $value;
		while (1) {
			print "$label ";
			$value = <STDIN>;
			exit 1 if !$value;
			chomp $value;
			if ($name eq "password" && !legal_password($value)) {
				print "$last_error\n";
				next;
			}
			last if $value =~ /\S+/;
		}
		$user_details{$name} = $value;
		print USER "$name=$value\n";
	}
	close(USER);
	print "Welcome to mekong.com.au, $login.\n";
	return $login;
}

sub search_command {
	my ($search_string) = @_;
	$search_string =~ s/\s*$//;
	$search_string =~ s/^\s*//;
	search_command1(split /\s+/, $search_string);
}

sub search_command1 {
	my (@search_terms) = @_;
	my @matching_isbns = search_books1(@search_terms);
	if ($last_error) {
		print "$last_error\n";
	} elsif (@matching_isbns) {
		print_books(@matching_isbns);
	} else {
		print "No books matched.\n";
	}
}

sub details_command {
	my ($isbn) = @_;
	our %book_details;
	if (!legal_isbn($isbn)) {
		print "$last_error\n";
		return;
	}
	if (!$book_details{$isbn}) {
		print "Unknown isbn: $isbn.\n";
		return;
	}
	print_books($isbn);
	foreach $attribute (sort keys %{$book_details{$isbn}}) {
		next if $attribute =~ /Image|=|^(|price|title|authors|productdescription)$/;
		print "$attribute: $book_details{$isbn}{$attribute}\n";
	}
	my $description = $book_details{$isbn}{productdescription} or return;
	$description =~ s/\s+/ /g;
	$description =~ s/\s*<p>\s*/\n\n/ig;
	while ($description =~ s/<([^">]*)"[^"]*"([^>]*)>/<$1 $2>/g) {}
	$description =~ s/(\s*)<[^>]+>(\s*)/$1 $2/g;
	$description =~ s/^\s*//g;
	$description =~ s/\s*$//g;
	print "$description\n";
}

sub basket_command {
	my ($login) = @_;
	my @basket_isbns = read_basket($login);
	if (!@basket_isbns) {
		print "Your shopping basket is empty.\n";
	} else {
		print_books(@basket_isbns);
		printf "Total: %11s\n", sprintf("\$%.2f", total_books(@basket_isbns));
	}
}

sub add_command {
	my ($login,$isbn) = @_;
	our %book_details;
	if (!legal_isbn($isbn)) {
		print "$last_error\n";
		return;
	}
	if (!$book_details{$isbn}) {
		print "Unknown isbn: $isbn.\n";
		return;
	}
	add_basket($login, $isbn);
}

sub drop_command {
	my ($login,$isbn) = @_;
	my @basket_isbns = read_basket($login);
	if (!legal_isbn($argument)) {
		print "$last_error\n";
		return;
	}
	if (!grep(/^$isbn$/, @basket_isbns)) {
		print "Isbn $isbn not in shopping basket.\n";
		return;
	}
	delete_basket($login, $isbn);
}

sub checkout_command {
	my ($login) = @_;
	my @basket_isbns = read_basket($login);
	if (!@basket_isbns) {
		print "Your shopping basket is empty.\n";
		return;
	}
	print "Shipping Details:\n$user_details{name}\n$user_details{street}\n$user_details{city}\n$user_details{state}, $user_details{postcode}\n\n";
	print_books(@basket_isbns);
	printf "Total: %11s\n", sprintf("\$%.2f", total_books(@basket_isbns));
	print "\n";
	my ($credit_card_number, $expiry_date);
	while (1) {
			print "Credit Card Number: ";
			$credit_card_number = <>;
			exit 1 if !$credit_card_number;
			$credit_card_number =~ s/\s//g;
			next if !$credit_card_number;
			last if $credit_card_number =~ /^\d{16}$/;
			last if legal_credit_card_number($credit_card_number);
			print "$last_error\n";
	}
	while (1) {
			print "Expiry date (mm/yy): ";
			$expiry_date = <>;
			exit 1 if !$expiry_date;
			$expiry_date =~ s/\s//g;
			next if !$expiry_date;
			last if legal_expiry_date($expiry_date);
			print "$last_error\n";
	}
	finalize_order($login, $credit_card_number, $expiry_date);
}

sub orders_command {
	my ($login) = @_;
	print "\n";
	foreach $order (login_to_orders($login)) {
		my ($order_time, $credit_card_number, $expiry_date, @isbns) = read_order($order);
		$order_time = localtime($order_time);
		print "Order #$order - $order_time\n";
		print "Credit Card Number: $credit_card_number (Expiry $expiry_date)\n";
		print_books(@isbns);
		print "\n";
	}
}

# print descriptions of specified books
sub print_books(@) {
	my @isbns = @_;
	print get_book_descriptions(@isbns);
}

# return descriptions of specified books
sub get_book_descriptions {
	my @isbns = @_;
	my $descriptions = "";
	our %book_details;
	foreach $isbn (@isbns) {
		die "Internal error: unknown isbn $isbn in print_books\n" if !$book_details{$isbn}; # shouldn't happen
		my $title = $book_details{$isbn}{title} || "";
		my $authors = $book_details{$isbn}{authors} || "";
		$authors =~ s/\n([^\n]*)$/ & $1/g;
		$authors =~ s/\n/, /g;
		$descriptions .= sprintf "%s %7s %s - %s\n", $isbn, $book_details{$isbn}{price}, $title, $authors;
	}
	return $descriptions;
}

sub set_global_variables {
	$base_dir = ".";
	$books_file = "$base_dir/books.json";
	$orders_dir = "$base_dir/orders";
	$baskets_dir = "$base_dir/baskets";
	$users_dir = "$base_dir/users";
	$last_error = "";
	%user_details = ();
	%book_details = ();
	%attribute_names = ();
	@new_account_rows = (
		  'login|Login:|10',
		  'password|Password:|10',
		  'name|Full Name:|50',
		  'street|Street:|50',
		  'city|City/Suburb:|25',
		  'state|State:|25',
		  'postcode|Postcode:|25',
		  'email|Email Address:|35'
		  );
}


sub incorrect_command_message {
	my ($command) = @_;
	print "Incorrect command: $command.\n";
	print <<eof;
Possible commands are:
login <login-name>
new_account <login-name>                    
search <words>
details <isbn>
add <isbn>
drop <isbn>
basket
checkout
orders
quit
eof
}


