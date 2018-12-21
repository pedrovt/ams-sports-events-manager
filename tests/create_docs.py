# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re

class AppDynamicsJob(unittest.TestCase):
    def setUp(self):
        # AppDynamics will automatically override this web driver
        # as documented in https://docs.appdynamics.com/display/PRO44/Write+Your+First+Script
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "https://www.katalon.com/"
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_app_dynamics_job(self):
        driver = self.driver
        driver.get("http://cityrunning.westeurope.cloudapp.azure.com:8080/see_documents?e_name=Futebol")
        driver.find_element_by_link_text("My Events").click()
        driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Futebol'])[1]/following::button[1]").click()
        driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Delete Event'])[1]/following::button[1]").click()
        driver.find_element_by_id("security_info").click()
        driver.find_element_by_id("security_info").clear()
        driver.find_element_by_id("security_info").send_keys("PSP")
        driver.find_element_by_id("health_info").click()
        driver.find_element_by_id("health_info").clear()
        driver.find_element_by_id("health_info").send_keys("INEM")
        driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Authority Name'])[1]/following::label[1]").click()
        driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Authority Name'])[2]/following::label[1]").click()
        driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Soon'])[1]/following::div[1]").click()
        driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Soon'])[1]/following::button[1]").click()
        driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Create Documents'])[1]/following::button[1]").click()
        driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='katalon'])[1]/following::button[1]").click()
    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e: return False
        return True
    
    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException as e: return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True
    
    def tearDown(self):
        # To know more about the difference between verify and assert,
        # visit https://www.seleniumhq.org/docs/06_test_design_considerations.jsp#validating-results
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
