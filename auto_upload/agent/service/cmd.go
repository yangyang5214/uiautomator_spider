package service

import (
	"fmt"
	"github.com/gin-gonic/gin"
	"github.com/spf13/viper"
	"net/http"
)

type CmdService struct {
}

func (s *CmdService) UploadFile(c *gin.Context) {
	var TargetDir = viper.GetString("target_dir")
	file, _ := c.FormFile("file")
	if file == nil {
		c.String(http.StatusBadRequest, "file is empty")
	}
	fmt.Printf("upload Filename: %s.\n", file.Filename)
	dst := TargetDir + "/" + file.Filename
	fmt.Printf("dst file path: %s.\n", dst)
	err := c.SaveUploadedFile(file, dst)
	if err != nil {
		c.String(http.StatusBadRequest, fmt.Sprintf("Save file %s error", dst))
	} else {
		c.String(http.StatusOK, fmt.Sprintf("'%s' uploaded!", file.Filename))
	}
}
