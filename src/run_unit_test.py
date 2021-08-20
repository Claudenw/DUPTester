import os
import argparse
import subprocess

curr_dir = os.path.dirname(os.path.abspath(__file__))
target_path = curr_dir + '/../test-migrator-based-python/base_file.py'
migrate_test = curr_dir + '/../test-migrator-based-python/multiple_tests_generator.py'
src_path = curr_dir + '/../test-migrator-based-python/generated_files'
cass_path = curr_dir + "/cass/"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the unit test for specific unit tests.',
        epilog='Example usage: python run_unit_test.py 16296')

    parser.add_argument("case_number", help="The number of the case you want to reproduce.")

    args = parser.parse_args()
    case_number = args.case_number

    #os.system("cp " + src_path + case_number + " " + src_path)
    os.system("cp " + target_path + case_number + " " + target_path)

    p1 = subprocess.Popen(["python", cass_path+"test_dispy/tmp.py"], cwd=cass_path+"test_dispy")
    out, err = p1.communicate()
    file_path = str(out)[:-1] + "/../dispynode.py"
    p2 = subprocess.Popen(["python", file_path, "--clean"])

    p3 = subprocess.Popen(["python3", migrate_test ])
    p3.wait()
    p = subprocess.Popen(["cp", "-r", src_path, curr + "/cass/generated_test"])

    p4 = subprocess.Popen(["python", cass_path+"parallel_test.py"])
    p4.wait()

    p2.kill()
