import pandas as pd
import os

def create_prepared_df() -> pd.DataFrame:
    summative_s1_df = pd.read_csv("../data/gradebook_semester_1.csv")
    summative_s2_df = pd.read_csv("../data/gradebook_semester_2.csv")
    formative_sec21_df = pd.read_csv("../data/end_of_semester_exam_formative_sec21.csv")
    formative_sec23_df = pd.read_csv("../data/end_of_semester_exam_formative_sec23.csv")
    formative_sec24_df = pd.read_csv("../data/end_of_semester_exam_formative_sec24.csv")

    summative_df = create_summative_df(summative_s1_df, summative_s2_df)

    formative_df = create_formative_df(formative_sec21_df, formative_sec23_df, formative_sec24_df)

    combined_df = pd.merge(summative_df, formative_df, on='student_id', how='outer')

    combined_df['End of Semester Test Raw Grade (7)'] = combined_df['End of Semester Test Raw'].apply(lambda x: get_grade(x))
    combined_df['End of Semester Test Curved Grade (7)'] = combined_df['End of Semester Test Curved (20%)'].apply(lambda x: get_grade(x))

    return combined_df 

def create_summative_df(summative_s1_df, summative_s2_df) -> pd.DataFrame:
    summative_s1_df = clean_summative_df_headers(summative_s1_df, 1)

    summative_s1_df = summative_s1_df.rename(columns={'Mid Semester Test Curved (20%)': 'Mid Semester Test Curved',
        'Criterion A PS Grade': 'Criterion A PS Grade (6)',
        'Criterion B PS Grade': 'Criterion B PS Grade (6)',
        'Criterion C PS Grade': 'Criterion C PS Grade (12)',
        'Criterin D PS Grade': 'Criterion D PS Grade (6)'})

    summative_s2_df = clean_summative_df_headers(summative_s2_df, 2)

    summative_s2_df = summative_s2_df.rename(columns={'Mid Semester Test Curved (30%)': 'Mid Semester Test Curved',
        'Criterin D PS Grade (6)': 'Criterion D PS Grade (6)'})

    summative_df = pd.concat([summative_s1_df, summative_s2_df], ignore_index=True)
    summative_df = summative_df.drop(['Project (B) 10%', 'Project (C) 15%', 'Project (D) 5%'], axis=1)

    return summative_df

def create_formative_df(formative_sec21_df, formative_sec23_df, formative_sec24_df) -> pd.DataFrame:
    formative_sec21_df = clean_formative_df_headers(formative_sec21_df)
    formative_sec21_df = drop_incorrect_rows_student_id(formative_sec21_df)

    formative_sec23_df = clean_formative_df_headers(formative_sec23_df)
    formative_sec23_df = drop_incorrect_rows_student_id(formative_sec23_df)

    formative_sec24_df = clean_formative_df_headers(formative_sec24_df)
    formative_sec24_df = drop_incorrect_rows_student_id(formative_sec24_df)

    formative_sec24_df.loc[formative_sec24_df['student_id'] == 'sec24_22', 'End of Semester Formative Score (18)'] = None
    formative_sec24_df.loc[formative_sec24_df['student_id'] == 'sec24_22', 'End of Semester Formative Score (%)'] = None
    formative_sec24_df.loc[formative_sec24_df['student_id'] == 'sec24_22', 'End of Semester Formative Grade (7)'] = None

    formative_df = pd.concat([formative_sec21_df, formative_sec23_df, formative_sec24_df], ignore_index=True)

    return formative_df

def clean_summative_df_headers(df, semester: int) -> pd.DataFrame:
    df.at[0, 'student_id'] = 'student_id'
    df.columns = df.iloc[0]
    df = df[1:]
    df = df.dropna(subset=['student_id'])
    df['semester'] = semester
    # This is header is the same in both datasets but is incorrectly labeled for semester 1 students as this actually represents 10% of Criterion A
    df = df.rename(columns={'Demo Completion (20%)': 'Demo Completion %'})
    return df

def clean_formative_df_headers(df) -> pd.DataFrame:
    df = df[['student_id', 'Unnamed: 5', 'Unnamed: 6', 'Unnamed: 7']]
    df = df.rename(columns={'Unnamed: 5': 'End of Semester Formative Score (18)', 
        'Unnamed: 6': 'End of Semester Formative Score (%)', 
        'Unnamed: 7': 'End of Semester Formative Grade (7)'})
    df = df.dropna(subset=['student_id'])
    return df

def drop_incorrect_rows_student_id(df):
    df = df.dropna(subset=['student_id'])
    to_drop = ['Section 21', 'Section 23', 'Section 24', 'Semester 1', 'Semester 2']
    df = df[~df['student_id'].isin(to_drop)]
    return df

def get_grade(percentage) -> int | None:
    try:
        percentage = int(percentage)
        if percentage >= 85:
            return 7
        elif percentage >= 75:
            return 6
        elif percentage >= 65:
            return 5
        elif percentage >= 55:
            return 4
        elif percentage >= 45:
            return 3
        elif percentage >= 35:
            return 2
        else:
            return 1
    except TypeError:
        return None
    
if __name__ == "__main__":
    df = create_prepared_df()