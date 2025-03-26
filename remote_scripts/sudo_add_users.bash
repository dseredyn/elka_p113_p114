if id "student-pl" >/dev/null 2>&1; then
    echo 'user found: student-pl'
else
    echo 'user not found: student-pl'
	useradd -m student-pl
	echo -e "student\nstudent" | passwd student-pl
fi

if id "student-en" >/dev/null 2>&1; then
    echo 'user found: student-en'
else
    echo 'user not found: student-en'
	useradd -m student-en
	echo -e "student\nstudent" | passwd student-en
fi
