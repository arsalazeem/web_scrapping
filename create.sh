rm -rf package
rm -rf my-deployment-package.zip
pip3 install --target ./package -r requirements.txt
pip install --target ./package -r lxml
cd package
zip -r ../my-deployment-package.zip .
cd ..
zip -g my-deployment-package.zip lambda_function.py

