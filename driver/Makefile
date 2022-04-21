NAME=bc125py-driver

all: $(NAME)

$(NAME): bc125py-driver.c
	$(CC) $(CFLAGS) -Wall -o $(NAME) $(NAME).c

install: all
	/usr/bin/install -o root -g wheel -t /usr/local/bin $(NAME)
	chmod 6755 /usr/local/bin/$(NAME)

uninstall: all
	rm /usr/local/bin/$(NAME)