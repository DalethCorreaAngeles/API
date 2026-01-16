APP_NAME=api-con-auth2
CHART_PATH=./api-con-auth2
VALUES=./api-con-auth2/	values.yaml

install:
	helm install $(APP_NAME) $(CHART_PATH) -f $(VALUES)

upgrade:
	helm upgrade $(APP_NAME) $(CHART_PATH) -f $(VALUES)

uninstall:
	helm uninstall $(APP_NAME)