mkdir /var/run/sshd

#ssh-keygen -q -N "" -t dsa -f /etc/ssh/ssh_host_dsa_key
#ssh-keygen -q -N "" -t rsa -f /etc/ssh/ssh_host_rsa_key
#ssh-keygen -q -N "" -t rsa -f /root/.ssh/id_rsa
#cp /root/.ssh/id_rsa.pub /root/.ssh/authorized_keys

ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
chmod 0600 ~/.ssh/authorized_keys

sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config
