<!-- Resume.svelte -->
<script>
  import '../../app.css'
  import { Progressbar } from 'flowbite-svelte';
  import TimelineCarousel from '../../lib/components/TimelineCarousel.svelte';
  import Timeline from '../../lib/components/Timeline.svelte';
  import Card from '../../lib/components/Card.svelte';
  import SoftSkills from '../../lib/components/SoftSkills.svelte';

  let programmingLanguages = [
    { skill: 'Python', progress: "75", level: "Advanced" },
    { skill: 'Rust', progress: "25", level: "Basic" },
    { skill: 'HTML,CSS,JS', progress: "50", level: "Intermediate" },
  ];

  let languages = [
    { skill: 'English', progress: "100", level: "Excellent" },
    { skill: 'German', progress: "50", level: "Intermediate" },
    { skill: 'Ukrainian', progress: "100", level: "Native" },
    { skill: 'Russian', progress: "100", level: "Native" },
  ];

  let workExperience = [
    {
      title: 'Mechanical Engineer',
      period: 'Nov 2018 - Apr 2019',
      description: 'Performed internship during bachelor degree. Designed special machinery for production lines on-site.',
      achievements: [
        'Developed prototypes using additive manufacturing techniques', 
        'Designed a full station for production line in Autodesk Inventor', 
        'Achievement 3'
      ],
      place: 'Robert Bosch GmbH',
      city: 'Stuttgart',
      country: 'Germany'
    },
    {
      title: 'Mechatronics Engineer',
      period: 'Jun 2022 - Sept 2022',
      description: 'Worked on research and development of a new eVTOL aircraft. (Internship during master degree)',
      achievements: [
        'Developed concepts for subsystems, based on requirements', 
        'Designed and constructed test benches', 
        'Performed flight testing'
      ],
      place: 'Volocopter GmbH',
      city: 'Munich',
      country: 'Germany'
    },
    {
      title: 'Fleet Reliability Engineer',
      period: 'Nov 2022 - Present',
      description: 'Enhanced internal procedures and fleet reliability, while achieving a significant expansion in fleet size and operational efficiency.',
      achievements: [
        'Automated internal procedures using Python and Rust', 
        'Developed internal tools to enhance fleet reliability', 
        'Developed set of microservices for automated issue reporting and debugging',
        'Scaled fleet by 10+ times'
      ],
      place: 'Qwello GmbH',
      city: 'Munich',
      country: 'Germany'
    },
  ];

  let education = [
    {
      title: 'B.Sc. Mechanical Engineering',
      period: 'Oct 2015 - Apr 2019',
      achievements: ['Major in automotive', 'Thesis: “Parcel delivery drone development”'],
      place: 'Karlsruhe Institute of Technology',
      city: 'Karlsruhe',
      country: 'Germany'
    },
    {
      title: 'M.Sc. Aerospace Engineering',
      period: 'Oct 2019 - Apr 2022',
      achievements: ['Major in control and real-time systems', 'Thesis: “Anomaly detection in telemetry using machine learning techniques”'],
      place: 'Technical University of Munich',
      city: 'Munich',
      country: 'Germany'
    },
  ];

  let tools = [
    { category: 'Project management', examples: 'Jira, Slack' },
    { category: 'Operating systems', examples: 'Linux, MacOS'},
    { category: 'Versioning control', examples: 'Git, GitHub, GitLab' },
    { category: 'Databases', examples: 'MySQL, PostgreSQL' },
    { category: 'Web frameworks', examples: 'Python (Django, FastAPI), Rust (Actix)' },
    { category: 'Cloud providers', examples: 'AWS, Linode'},
    { category: 'CI/CD', examples: 'GitLab CI/CD, GitHub Actions' },
    { category: 'Web hosting', examples: 'Terraform, Docker, Nginx' },
  ];

  let softSkills = [
    { skill: 'Fast learner', icon: 'fa-solid fa-graduation-cap', description: 'Able to absorb new information and integrate it effectively' },
    { skill: 'Teamwork', icon: 'fa-solid fa-user-group', description: 'Able to collaborate in diverse teams.' },
    { skill: 'Communication', icon: 'fa-solid fa-people-arrows', description: 'Effective in verbal and written communication.' },
    { skill: 'Problem-Solving', icon: 'fa-solid fa-circle-xmark', description: 'Excellent at identifying solutions in challenging situations.' },
  ]

  async function downloadPDF() {
    try {
      const response = await fetch('api/download?title=Resume');
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      // the filename you want
      a.download = 'CV_mykyta_prokaiev.pdf';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('There was an error downloading the file:', error);
    }
}
</script>

<div class="mt-20 w-full md:w-3/5 lg:w-1/2 py-4">
  <!-- About Me Section -->
  <div>
    <section class="p-6 mx-auto max-w-4xl">
      <div class="flex flex-col items-center text-center space-y-4 mb-10">
        <h1 class="text-2xl font-semibold text-secondary">Mykyta Prokaiev</h1>
        <p class="text-md text-accent">Software developer</p>
      </div>
      <div class="text-center mt-4">
        <button  class="custom-btn" on:click={downloadPDF}>Download Resume</button>
      </div>
    </section>
  </div>

  <!-- Work Experience Section -->
  <section>
    <TimelineCarousel items={workExperience} header="Work Experience" />
  </section>

  <!-- Education Section -->
  <section>
    <TimelineCarousel items={education} header="Education"/>
  </section>

  <!-- Programming language Section -->
  <section >
    <h2 class="section-header">Programming languages</h2>
    {#each programmingLanguages as language}
    <div class="my-8">
      <div class="flex justify-between mb-1 ">
        <div class="font-medium text-accent">{language.skill}</div>
        <div class="font-medium text-secondary">{language.level}</div>
      </div>
      <Progressbar progress={language.progress} color="gray" divClass="bg-none" size="h-2.5 rounded-none"/>
    </div>
    {/each}
  </section>

  <!-- Frameworks and Tools Section -->
  <section>
    <h2 class="section-header">Frameworks & Tools</h2>
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
    {#each tools as item, _}
      <Card item={item} />
    {/each}
  </section>


   <!-- Language Section -->
   <section>
    <h2 class="section-header">Languages</h2>
    {#each languages as language}
    <div class="my-8">
      <div class="flex justify-between mb-1 ">
        <div class="font-medium text-accent">{language.skill}</div>
        <div class="font-medium text-secondary">{language.level}</div>
      </div>
      <Progressbar progress={language.progress} color="gray" divClass="bg-none" size="h-2.5 rounded-none" />
    </div>
    {/each}
  </section>

  <!-- Soft Skills Section -->
  <section>
    <h2 class="section-header">Soft Skills</h2>

      <SoftSkills items={softSkills}/>
  </section>

</div>


