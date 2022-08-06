package main

import (
	"github.com/gin-gonic/gin"
	"github.com/spf13/viper"
	"spider_agent/service"
)

func main() {
	router := gin.Default()

	viper.AddConfigPath(".")
	viper.SetConfigName("config")
	err := viper.ReadInConfig()
	if err != nil {
		panic(err)
	}

	router.GET("/ping", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"message": "hello pvp win agent!",
		})
	})

	cmdService := service.CmdService{}
	cmdRouter := router.Group("/spider")
	router.Use(gin.BasicAuth(gin.Accounts{
		"up_agent": "hdd_20220804~",
	}))

	{
		cmdRouter.POST("upload", cmdService.UploadFile)
	}

	err = router.Run(":9991")
	if err != nil {
		panic(err)
	}
}
