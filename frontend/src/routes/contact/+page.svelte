<script>
  
  import { onMount } from 'svelte';
  import { createForm } from "svelte-forms-lib";
  import { Label, Input, Textarea, Helper } from 'flowbite-svelte';
  import "../../app.css";
  import * as yup from "yup";

  let grecaptchaclient;
  let isRecaptchaValid = false;
  let isFormTouched = false;
  let grecaptchaLoaded = false;
  let successMessage = "";
  
  onMount(async () => {
    let checkRecaptcha = setInterval(() => {
      if (window.grecaptcha && window.grecaptcha.ready) {
        window.grecaptcha.ready(() => {
          grecaptchaclient = grecaptcha.render('recaptchabox', {
            'sitekey': '6Ldg_DgpAAAAAPAyrh_wAnpbH17B6aktDZlZV_fL',
            'size': 'normal',
            'callback': () => {
              isRecaptchaValid = grecaptcha.getResponse(grecaptchaclient) !== '';
            }
          });
          clearInterval(checkRecaptcha);
        });
        grecaptchaLoaded = true;
      }
    }, 100); // Check every 100ms

    // Set a timeout to clear the interval after 5 seconds
    const timeout = setTimeout(() => {
      clearInterval(checkRecaptcha);
    }, 5000);

    return () => {
      clearTimeout(timeout);
      clearInterval(checkRecaptcha);
    };
  });


  const sendForm = async ({name, email, message}) => {
    const token = await grecaptcha.getResponse(grecaptchaclient);
    await fetch('/api/contacts/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name, email, message, recaptcha: token })

    })
    .then(async response => {
      const result = await response.json();
      successMessage = result.message;
      handleReset();
      grecaptcha.reset(grecaptchaclient); 
    })
    .catch(async error => {
      console.error('Error:', await error)
    });
  }

  
  const {
    // observables state
    form,
    errors,
    state,
    touched,
    isValid,
    isSubmitting,
    isValidating,
    // handlers
    handleBlur,
    handleReset,
    handleChange,
    handleSubmit
  } = createForm({
    initialValues: {
      name: "",
      email: "",
      message: ""
    },
    validationSchema: yup.object().shape({
      name: yup.string().required(),
      email: yup
        .string()
        .email()
        .required(),
      message: yup.string().required()
    }),
    onSubmit: values => {
      return sendForm(values).catch((e) => {
        alert(e);
      })
    }
  });

  const updateDirtyState = () => {
    isFormTouched = $form.name !== "" ||
                  $form.email !== ""||
                  $form.message !== "";
  };

  $: updateDirtyState();

</script>

<svelte:head>
<script src="https://www.google.com/recaptcha/api.js" async defer>
</script>
</svelte:head>

<form class="my-20 p-4 bg-base-100 sm:w-full md:w-1/2 lg:w-2/5" class:valid={$isValid && isRecaptchaValid} on:submit={handleSubmit}>
  <div class="form-control  py-2">
    <Label for="name" class="label">
      <span class="label-text text-secondary">Name</span>
    </Label>
    <Input 
      id="name" 
      class="rounded-none bg-primary border-secondary"
      name="name" 
      type="text" 
      on:keyup={handleChange} 
      on:change={updateDirtyState} 
      bind:value={$form.name}
      required/>
    {#if $errors.name && $touched.name}
      <Helper class="text-accent">{$errors.name}</Helper>
    {/if}
  </div>
  <div class="form-control  py-2">
    <Label for="email" class="label">
      <span class="label-text text-secondary">Email</span>
    </Label>
    <Input 
      id="email" 
      class="rounded-none bg-primary border-secondary" 
      name="email" 
      type="email" 
      on:keyup={handleChange} 
      on:change={updateDirtyState} 
      bind:value={$form.email}
      required/>
    {#if $errors.email && $touched.email}
      <Helper class="text-accent">{$errors.email}</Helper>
    {/if}
  </div>
  <div class="form-control py-2">
    <Label for="message" class="label">
      <span class="label-text text-secondary">Message</span>
    </Label>
    <Textarea 
      id="message" 
      name="message" 
      class="rounded-none bg-primary border-secondary"  
      rows=10
      placeholder= 'Leave a your message here...'
      on:keyup={handleChange} 
      on:change={updateDirtyState}
      bind:value={$form.message}
      required></Textarea>
    {#if $errors.message && $touched.message}
      <Helper class="text-accent">{$errors.message}</Helper>
    {/if}
  </div>
  <div id="recaptchabox" class="py-4"></div>
  <button type="submit" class="submit-button px-10 py-2 border-2" disabled={!isRecaptchaValid || !$isValid || !isFormTouched}>Submit</button>
  {#if successMessage}
    <div class="text-accent mt-4">
      {successMessage}
    </div>
  {/if}
</form>





<style>
  .submit-button:valid {
    @apply text-secondary bg-primary border-secondary;
  }
  .submit-button:valid:hover{
    @apply text-primary bg-accent border-accent;
  }
  .submit-button:disabled {
    background: grey;
  }
</style>


