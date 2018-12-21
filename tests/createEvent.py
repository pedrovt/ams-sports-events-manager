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
        driver.get("http://cityrunning.westeurope.cloudapp.azure.com:8080/my_events")
        driver.find_element_by_link_text(u"Create a new event »").click()
        driver.find_element_by_id("id_e_name").click()
        driver.find_element_by_id("id_e_name").clear()
        driver.find_element_by_id("id_e_name").send_keys("Festas na UA")
        driver.find_element_by_id("id_e_date_end").click()
        driver.find_element_by_id("id_e_date_end").click()
        driver.find_element_by_id("id_e_date_end").clear()
        driver.find_element_by_id("id_e_date_end").send_keys("2018-12-25")
        driver.find_element_by_name("e_date").click()
        driver.find_element_by_name("e_date").click()
        driver.find_element_by_name("e_date").clear()
        driver.find_element_by_name("e_date").send_keys("2018-12-31")
        driver.find_element_by_id("id_e_place").click()
        driver.find_element_by_id("id_e_place").clear()
        driver.find_element_by_id("id_e_place").send_keys("Universidade de Aveiro")
        driver.find_element_by_id("id_e_mod").click()
        driver.find_element_by_id("id_e_part").click()
        Select(driver.find_element_by_id("id_e_part")).select_by_visible_text("Large (100+ participants)")
        driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Icon (Soon)'])[1]/following::input[1]").click()
    
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
