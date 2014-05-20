#!/bin/bash
mkdir /var/lib/check.d

echo "#!/bin/bash" > /var/lib/check.d/1.sh
echo "echo \"OK\" " >> /var/lib/check.d/1.sh
chmod u+x /var/lib/check.d/1.sh

echo "#!/bin/bash" > /var/lib/check.d/2.sh
echo "echo \"60 %\"" >> /var/lib/check.d/2.sh
chmod u+x /var/lib/check.d/2.sh

echo "#!/bin/bash" > /var/lib/check.d/3.sh
echo "echo \"90 %\"" >> /var/lib/check.d/3.sh
chmod u+x /var/lib/check.d/3.sh

echo "[test1]" > /var/lib/check.d/test.cfg
echo "check=/var/lib/check.d/1.sh" >> /var/lib/check.d/test.cfg
echo "type=ok"  >> /var/lib/check.d/test.cfg
echo "[test2]"  >> /var/lib/check.d/test.cfg
echo "check=/var/lib/check.d/2.sh"  >> /var/lib/check.d/test.cfg
echo "type=above"  >> /var/lib/check.d/test.cfg
echo "threshold=50"  >> /var/lib/check.d/test.cfg
echo "[test3]"  >> /var/lib/check.d/test.cfg
echo "check=/var/lib/check.d/3.sh"  >> /var/lib/check.d/test.cfg
echo "type=below"  >> /var/lib/check.d/test.cfg
echo "threshold=50" >> /var/lib/check.d/test.cfg

echo "DONE"
